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

    def __init__(self, numnodes, maxretries, log=None):
        self.numnodes = numnodes
        self.maxretries = maxretries
        self.node2collection = {}
        self.node2pending = {}
        self.node2retries = {}
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
        self.node2retries[node] = {}

    def tests_finished(self):
        """Return True if all tests have been executed by the nodes."""
        if not self.collection_is_completed:
            return False
        if self.pending:
            return False
        for retries in self.node2retries.values():
            if retries:
                return False
        for pending in self.node2pending.values():
            if pending:
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

    def update_item(self, node, item_index, failed):
        self.node2pending[node].remove(item_index)

        if failed:
            nretries = self.node2retries[node].get(item_index, 0)
            if nretries < self.maxretries:
                self.node2retries[node][item_index] = nretries + 1
                # re-add to the end of the list for the node
                self.node2pending[node].append(item_index)
                node.send_runtest_some([item_index])
                return True
        self.node2retries[node].pop(item_index, None)

        if not self.node2pending[node] and not self.node2retries[node]:
            self.dispatch_next_test_class(node)
        return False

    def dispatch_next_test_class(self, node, duration=0):
        """
            Dispatch the test methods for a single test class to a node
        """
        if not self.pending:
            return

        classprefix, _, _ = self.collection[self.pending[0]].rpartition("::")
        batchsize = 1
        while batchsize < len(self.pending) and self.collection[self.pending[batchsize]].startswith(classprefix):
            batchsize += 1
        self._send_tests(node, batchsize)

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
        return crashitem

    def init_distribute(self):
        """Initiate distribution of the test collection

        Initiate scheduling of the items across the nodes.

        This is called by the ``DSession.slave_collectionfinish`` hook
        if ``.collection_is_completed`` is True.

        XXX Perhaps this method should have been called ".schedule()".
        """
        assert self.collection_is_completed

        # XXX allow nodes to have different collections
        if not self._check_nodes_have_same_collection():
            self.log('**Different tests collected, aborting run**')
            return

        # Collections are identical, create the index of pending items.
        self.collection = list(self.node2collection.values())[0]
        self.pending[:] = range(len(self.collection))
        if not self.collection:
            return

        # Start sending tests to each available node
        for node in self.nodes:
            self.dispatch_next_test_class(node)

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
