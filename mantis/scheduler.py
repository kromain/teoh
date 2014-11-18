import difflib

import pytest
import py


class TargetScheduler:
    """Implement load scheduling accross targets.

    Currently based on pytest-xdist's LoadScheduling in dsession.py

    This distributes the tests collected across all nodes so each test
    is run just once.  All nodes collect and submit the test suit and
    when all collections are received it is verified they are
    identical collections.  Then the collection gets devided up in
    chunks and chunks get submitted to nodes.  Whenver a node finishes
    an item they call ``.remove_item()`` which will trigger the
    scheduler to assign more tests if the number of pending tests for
    the node falls below a low-watermark.

    When created ``numnodes`` defines how many nodes are expected to
    submit a collection, this is used to know when all nodes have
    finished collection or how large the chunks need to be created.

    Attributes:

    :numnodes: The expected number of nodes taking part.  The actual
       number of nodes will vary during the scheduler's lifetime as
       nodes are added by the DSession as they are brought up and
       removed either because of a died node or normal shutdown.  This
       number is primarily used to know when the initial collection is
       completed.

    :node2collection: Map of nodes and their test collection.  All
       collections should always be identical.

    :node2pending: Map of nodes and the indices of their pending
       tests.  The indices are an index into ``.pending`` (which is
       identical to their own collection stored in
       ``.node2collection``).

    :collection: The one collection once it is validated to be
       identical between all the nodes.  It is initialised to None
       until ``.init_distribute()`` is called.

    :pending: List of indices of globally pending tests.  These are
       tests which have not yet been allocated to a chunk for a node
       to process.

    :log: A py.log.Producer instance.

    """

    def __init__(self, numnodes, log=None):
        self.numnodes = numnodes
        self.node2collection = {}
        self.node2pending = {}
        self.pending = []
        self.collection = None
        if log is None:
            self.log = py.log.Producer("loadsched")
        else:
            self.log = log.loadsched

    @property
    def nodes(self):
        """A list of all nodes in the scheduler."""
        return list(self.node2pending.keys())

    @property
    def collection_is_completed(self):
        """Boolean indication initial test collection is complete.

        This is a boolean indicating all initial participating nodes
        have finished collection.  The required number of initial
        nodes is defined by ``.numnodes``.
        """
        return len(self.node2collection) >= self.numnodes

    def haspending(self):
        """Return True if there are pending test items

        This indicates that collection has finished and nodes are
        still processing test items, so can be thought of as "the
        scheduler is active".
        """
        if self.pending:
            return True
        for pending in self.node2pending.values():
            if pending:
                return True
        return False

    def hasnodes(self):
        """Return True if nodes exist in the scheduler."""
        return bool(self.node2pending)

    def addnode(self, node):
        """Add a new node in the scheduler.

        From now on the node will be allocated chunks of tests to
        execute.

        Called by the ``DSession.slave_slaveready`` hook when it
        sucessfully bootstrapped a new node.
        """
        assert node not in self.node2pending
        self.node2pending[node] = []

    def tests_finished(self):
        """Return True if all tests have been executed by the nodes."""
        if not self.collection_is_completed:
            return False
        if self.pending:
            return False
        for pending in self.node2pending.values():
            if len(pending) >= 2:
                return False
        return True

    def addnode_collection(self, node, collection):
        """Add the collected test items from a node

        The collection is stored in the ``.node2collection`` map.
        Called by the ``DSession.slave_collectionfinish`` hook.
        """
        assert node in self.node2pending
        if self.collection_is_completed:
            # A new node has been added later, perhaps an original one died.
            assert self.collection  # .init_distribute() should have
                                    # been called by now
            if collection != self.collection:
                other_node = next(iter(self.node2collection.keys()))
                msg = report_collection_diff(self.collection,
                                             collection,
                                             other_node.gateway.id,
                                             node.gateway.id)
                self.log(msg)
                return
        self.node2collection[node] = list(collection)

    def remove_item(self, node, item_index, duration=0):
        """Mark test item as completed by node

        The duration it took to execute the item is used as a hint to
        the scheduler.

        This is called by the ``DSession.slave_testreport`` hook.
        """
        self.node2pending[node].remove(item_index)
        self.check_schedule(node, duration=duration)

    def check_schedule(self, node, duration=0):
        """Maybe schedule new items on the node

        If there are any globally pending nodes left then this will
        check if the given node should be given any more tests.  The
        ``duration`` of the last test is optionally used as a
        heuristic to influence how many tests the node is assigned.
        """
        if self.pending:
            # how many nodes do we have?
            num_nodes = len(self.node2pending)
            # if our node goes below a heuristic minimum, fill it out to
            # heuristic maximum
            items_per_node_min = max(2, len(self.pending) // num_nodes // 4)
            items_per_node_max = max(2, len(self.pending) // num_nodes // 2)
            node_pending = self.node2pending[node]
            if len(node_pending) < items_per_node_min:
                if duration >= 0.1 and len(node_pending) >= 2:
                    # seems the node is doing long-running tests
                    # and has enough items to continue
                    # so let's rather wait with sending new items
                    return
                num_send = items_per_node_max - len(node_pending)
                self._send_tests(node, num_send)
        self.log("num items waiting for node:", len(self.pending))

    def remove_node(self, node):
        """Remove an node from the scheduler

        This should be called either when the node crashed or at
        shutdown time.  In the former case any pending items assigned
        to the node will be re-scheduled.  Called by the
        ``DSession.slave_slavefinished`` and
        ``DSession.slave_errordown`` hooks.

        Return the item which was being executing while the node
        crashed or None if the node has no more pending items.

        """
        pending = self.node2pending.pop(node)
        if not pending:
            return

        # The node crashed, reassing pending items
        crashitem = self.collection[pending.pop(0)]
        self.pending.extend(pending)
        for node in self.node2pending:
            self.check_schedule(node)
        return crashitem

    def init_distribute(self):
        """Initiate distribution of the test collection

        Initiate scheduling of the items across the nodes.  If this
        gets called again later it behaves the same as calling
        ``.check_schedule()`` on all nodes so that newly added nodes
        will start to be used.

        This is called by the ``DSession.slave_collectionfinish`` hook
        if ``.collection_is_completed`` is True.

        XXX Perhaps this method should have been called ".schedule()".
        """
        assert self.collection_is_completed

        # Initial distribution already happend, reschedule on all nodes
        if self.collection is not None:
            for node in self.nodes:
                self.check_schedule(node)
            return

        # XXX allow nodes to have different collections
        if not self._check_nodes_have_same_collection():
            self.log('**Different tests collected, aborting run**')
            return

        # Collections are identical, create the index of pending items.
        self.collection = list(self.node2collection.values())[0]
        self.pending[:] = range(len(self.collection))
        if not self.collection:
            return

        # how many items per node do we have about?
        items_per_node = len(self.collection) // len(self.node2pending)
        # take a fraction of tests for initial distribution
        node_chunksize = max(items_per_node // 4, 2)
        # and initialize each node with a chunk of tests
        for node in self.nodes:
            self._send_tests(node, node_chunksize)

    def _send_tests(self, node, num):
        tests_per_node = self.pending[:num]
        if tests_per_node:
            del self.pending[:num]
            self.node2pending[node].extend(tests_per_node)
            node.send_runtest_some(tests_per_node)

    def _check_nodes_have_same_collection(self):
        """Return True if all nodes have collected the same items.

        If collections differ this returns False and logs the
        collection differences as they are found.
        """
        node_collection_items = list(self.node2collection.items())
        first_node, col = node_collection_items[0]
        same_collection = True
        for node, collection in node_collection_items[1:]:
            msg = report_collection_diff(
                col,
                collection,
                first_node.gateway.id,
                node.gateway.id,
            )
            if msg:
                self.log(msg)
                same_collection = False

        return same_collection

def report_collection_diff(from_collection, to_collection, from_id, to_id):
    """Report the collected test difference between two nodes.

    :returns: detailed message describing the difference between the given
    collections, or None if they are equal.
    """
    if from_collection == to_collection:
        return None

    diff = difflib.unified_diff(
        from_collection,
        to_collection,
        fromfile=from_id,
        tofile=to_id,
    )
    error_message = py.builtin._totext(
        'Different tests were collected between {from_id} and {to_id}. '
        'The difference is:\n'
        '{diff}'
    ).format(from_id=from_id, to_id=to_id, diff='\n'.join(diff))
    msg = "\n".join([x.rstrip() for x in error_message.split("\n")])
    return msg
