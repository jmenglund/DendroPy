#! /usr/bin/env python

##############################################################################
##  DendroPy Phylogenetic Computing Library.
##
##  Copyright 2010-2014 Jeet Sukumaran and Mark T. Holder.
##  All rights reserved.
##
##  See "LICENSE.txt" for terms and conditions of usage.
##
##  If you use this work or any portion thereof in published work,
##  please cite it as:
##
##     Sukumaran, J. and M. T. Holder. 2010. DendroPy: a Python library
##     for phylogenetic computing. Bioinformatics 26: 1569-1571.
##
##############################################################################

"""
Taxon management.

Operation taxonomic unit concepts are essentially names for taxa in the "real
world". Operational taxonomic unit concepts are organized into taxonomic
namespaces. A taxonomic namespace is a self-contained and
functionally-complete collection of mutually-distinct operational taxonomic
unit concepts, and provide the semantic context in which operational taxonomic
units from across various data sources of different formats and provenances can
be related through correct interpretation of their taxon labels.

    * Operational taxonomic units are modeled by a :class:`Taxon` object.

    * Taxonomic namespaces, in which operational taxonomic units are organized,
      are modeled by a :class:`TaxonNamespace` object.

    * A :class:`TaxonNamespace` manages a collection of :class:`Taxon` objects, where each
      object represents a distinct operational taxonomic unit concept within
      the taxonomic namespace represented by that :class:`TaxonNamespace` object.

    * Each :class:`Taxon` object can belong to one and only one :class:`TaxonNamespace`:
      :class:`Taxon` objects are not shared across :class:`TaxonNamespace` objects.

    * Each :class:`Taxon` object has an attribute, `label`, whose (string) value
      is the name of the operational taxon unit concept that it represents.

    * Different :class:`Taxon` objects represent different operational taxonomic
      unit concepts, even if they have the same label value.

    * All client objects (:class:`TaxonNamespaceAssociated` objects) that reference
      the same :class:`TaxonNamespace` reference the same "universe" or domain of
      operational taxonomic unit concepts.

    * Operational taxonomic units from across different data sources are mapped
      to distinct :class:`Taxon` objects within a particular :class:`TaxonNamespace` based on
      matching the string values of labels of the :class:`Taxon` object.

    * A particular taxonomic unit concept in one data source will only be
      correctly related to the same taxonomic unit concept (i.e, the same
      :class:`Taxon` object) in another data source only if they have both
      been parsed with reference to the same taxonomic namespace (i.e., the
      same :class:`TaxonNamespace` has been used).

    * A :class:`TaxonNamespace` assigned an "accession index" to every :class:`Taxon` object
      added to it. This is a stable and unique number within the context of any
      given :class:`TaxonNamespace` object (though a :class:`Taxon` object may have different
      accession indexes in different :class:`TaxonNamespace` objects if it
      belongs to multiple namespaces). This number is will be used to
      calculate the "split bitmask" hash of the trivial split or external edge
      subtending the node to which this :class:`Taxon` object is assigned on a tree.
      The concept of a "split bitmask" hash is fundamental to DendroPy's tree
      operations. The split bitmask is a hash that uniquely identifies every
      split on a tree.  It is calculated by OR'ing the split bitmask of all the
      child splits of the given split. Terminal edges, of course, do not have
      child edges, and their split bitmask is given by the accession index of
      the :class:`Taxon` object at their head or target nodes.
"""


import warnings
import collections
import copy
try:
    from StringIO import StringIO # Python 2 legacy support: StringIO in this module is the one needed (not io)
except ImportError:
    from io import StringIO # Python 3
from dendropy.datamodel import basemodel
from dendropy.utility import bitprocessing
from dendropy.utility import textprocessing
from dendropy.utility import container
from dendropy.utility import error
from dendropy.utility import deprecate

##############################################################################
## Helper functions

def taxon_set_deprecation_warning(stacklevel=6):
    deprecate.dendropy_deprecation_warning(
            message="Deprecated since DendroPy 4: 'taxon_set' will no longer be supported in future releases; use 'taxon_namespace' instead",
            stacklevel=stacklevel)

def process_kwargs_dict_for_taxon_namespace(kwargs_dict, default=None):
    if "taxon_set" in kwargs_dict:
        if "taxon_namespace" in kwargs_dict:
            raise TypeError("Cannot specify both 'taxon_namespace' and 'taxon_set' (legacy support) simultaneously")
        else:
            taxon_set_deprecation_warning()
            return kwargs_dict.pop("taxon_set", default)
    else:
        return kwargs_dict.pop("taxon_namespace", default)

def process_attached_taxon_namespace_directives(kwargs_dict):
    """
    The following idioms are supported:

        `taxon_namespace=tns`
            Attach `tns` as the bound (single, unified) taxonomic namespace
            reference for all objects.
        `attached_taxon_namespace=tns`
            Attach `tns` as the bound (single, unified) taxonomic namespace
            reference for all objects.
        `attach_taxon_namespace=True, attached_taxon_namespace=tns`
            Attach `tns` as the bound (single, unified) taxonomic namespace
            reference for all objects.
        `attach_taxon_namespace=True`
            Create a *new* :class:`TaxonNamespace` and set it as the bound
            (single, unified) taxonomic namespace reference for all
            objects.
    """
    deprecated_kw = [
            "taxon_namespace",
            "attach_taxon_namespace",
            "attached_taxon_namespace",
            "taxon_set",
            "attach_taxon_set",
            "attached_taxon_set",
            ]
    for kw in deprecated_kw:
        if kw in kwargs_dict:
            raise TypeError("'{}' is no longer supported as a keyword argument. Use the instance method 'attach_taxon_namespace()' of the data object instead".format(kw))
    taxon_namespace = None
    attach_taxon_namespace = False
    if ( ("taxon_set" in kwargs_dict or "taxon_namespace" in kwargs_dict)
            and ("attached_taxon_set" in kwargs_dict or "attached_taxon_namespace" in kwargs_dict)
            ):
        raise TypeError("Cannot specify both 'taxon_namespace'/'taxon_set' and 'attached_taxon_namespace'/'attached_taxon_set' together")
    if "taxon_set" in kwargs_dict:
        if "taxon_namespace" in kwargs_dict:
            raise TypeError("Both 'taxon_namespace' and 'taxon_set' cannot be specified simultaneously: use 'taxon_namespace' ('taxon_set' is only supported for legacy reasons)")
        kwargs_dict["taxon_namespace"] = kwargs_dict["taxon_set"]
        del kwargs_dict["taxon_set"]
    if "attached_taxon_set" in kwargs_dict:
        if "attached_taxon_namespace" in kwargs_dict:
            raise TypeError("Both 'attached_taxon_namespace' and 'attached_taxon_set' cannot be specified simultaneously: use 'attached_taxon_namespace' ('attached_taxon_set' is only supported for legacy reasons)")
        kwargs_dict["attached_taxon_namespace"] = kwargs_dict["attached_taxon_set"]
        del kwargs_dict["attached_taxon_set"]
    if "taxon_namespace" in kwargs_dict:
        taxon_namespace = kwargs_dict.pop("taxon_namespace", None)
        attach_taxon_namespace = True
    elif "attached_taxon_namespace" in kwargs_dict:
        taxon_namespace = kwargs_dict["attached_taxon_namespace"]
        if not isinstance(taxon_namespace, TaxonNamespace):
            raise TypeError("'attached_taxon_namespace' argument must be an instance of TaxonNamespace")
        attach_taxon_namespace = True
    else:
        taxon_namespace = None
        attach_taxon_namespace = kwargs_dict.get("attach_taxon_namespace", False)
    kwargs_dict.pop("taxon_namespace", None)
    kwargs_dict.pop("attach_taxon_namespace", None)
    kwargs_dict.pop("attached_taxon_namespace", None)
    return (attach_taxon_namespace, taxon_namespace)

##############################################################################
## TaxonNamespaceAssociated

class TaxonNamespaceAssociated(object):
    """
    Provides infrastructure for the maintenance of references to taxa.
    """

    # def initialize_taxon_namespace_from_kwargs_dict(self, kwargs_dict):
    #     tns = process_kwargs_dict_for_taxon_namespace(kwargs_dict)
    #     if tns is None:
    #         self.taxon_namespace = TaxonNamespace()
    #     else:
    #         self.taxon_namespace = tns
    #     return self.taxon_namespace

    def __init__(self, taxon_namespace=None):
        if taxon_namespace is None:
            self._taxon_namespace = TaxonNamespace()
        else:
            self._taxon_namespace = taxon_namespace
        self.automigrate_taxon_namespace_on_assignment = False

    def _get_taxon_namespace(self):
        return self._taxon_namespace
    def _set_taxon_namespace(self, tns):
        if self.automigrate_taxon_namespace_on_assignment:
            if tns is not None and self._taxon_namespace is not tns:
                self.migrate_taxon_namespace(tns)
            elif tns is None:
                self._taxon_namespace = None
        else:
            self._taxon_namespace = tns
    def _del_taxon_namespace(self):
        raise TypeError("Cannot delete 'taxon_namespace' attribute")
    taxon_namespace = property(_get_taxon_namespace, _set_taxon_namespace, _del_taxon_namespace)

    def _get_taxon_set(self):
        # raise NotImplementedError("'taxon_set' is no longer supported: use 'taxon_namespace' instead")
        taxon_set_deprecation_warning()
        return self.taxon_namespace
    def _set_taxon_set(self, v):
        # raise NotImplementedError("'taxon_set' is no longer supported: use 'taxon_namespace' instead")
        taxon_set_deprecation_warning()
        self.taxon_namespace = v
    def _del_taxon_set(self):
        # raise NotImplementedError("'taxon_set' is no longer supported: use 'taxon_namespace' instead")
        taxon_set_deprecation_warning()
    taxon_set = property(_get_taxon_set, _set_taxon_set, _del_taxon_set)

    def migrate_taxon_namespace(self,
            taxon_namespace,
            unify_taxa_by_label=True,
            case_sensitive_label_mapping=True,
            taxon_mapping_memo=None):
        """
        Move this object and all members to a new operational taxonomic unit
        concept namespace scope.

        Current :attr:`self.taxon_namespace` value will be replaced with value
        given in `taxon_namespace` if this is not `None`, or a new
        :class:`TaxonNamespace` object. Following this,
        `reconstruct_taxon_namespace()` will be called: each distinct
        :class:`Taxon` object associated with `self` or members of `self` that
        is not alread in `taxon_namespace` will be replaced with a new
        :class:`Taxon` object that will be created with the same label and
        added to :attr:`self.taxon_namespace`.  Calling this method results in
        the object (and all its member objects) being associated with a new,
        independent taxon namespace.

        Parameters
        ----------
        taxon_namespace : :class:`TaxonNamespace`
            The :class:`TaxonNamespace` into the scope of which this object
            will be moved.

        unify_taxa_by_label : boolean, optional
            If `True`, then references to distinct :class:`Taxon` objects with
            identical labels in the current namespace will be replaced with a
            reference to a single :class:`Taxon` object in the new namespace.
            If `False`: references to distinct :class:`Taxon` objects will
            remain distinct, even if the labels are the same.

        case_sensitive_label_mapping : boolean, optional
            If `False` and `unify_taxa_by_label` is also `True`, then the
            establishment of correspondence between :class:`Taxon` objects in
            the old and new namespaces with be based on case-insensitive
            matching of labels. E.g., if there are four :class:`Taxon` objects with
            labels 'Foo', 'Foo', 'FOO', and 'FoO' in the old namespace, then
            all objects that reference these will reference a single
            new :class:`Taxon` object in the new namespace (with a label some
            existing casing variant of 'foo'). Defaults to `True`:
            if `unify_taxa_by_label` is `True`, :class:`Taxon` objects with
            labels identical except in case will be considered distinct.

        taxon_mapping_memo : dictionary
            Similar to `memo` of deepcopy, this is a dictionary that maps
            :class:`Taxon` objects in the old namespace to corresponding
            :class:`Taxon` objects in the new namespace. Mostly for interal
            use when migrating complex data to a new namespace. Note that
            any mappings here take precedence over all other options: if a
            :class:`Taxon` object in the old namespace is found in this
            dictionary, the counterpart in the new namespace will be whatever
            value is mapped, regardless of, e.g. label values.

        Examples
        --------
        Use this method to move an object from one taxon namespace to
        another.

        For example, to get a copy of an object associated with another taxon
        namespace and associate it with a different namespace::

            # Get handle to the new TaxonNamespace
            other_taxon_namespace = some_other_data.taxon_namespace

            # Get a taxon-namespace scoped copy of a tree
            # in another namespace
            t2 = Tree(t1)

            # Replace taxon namespace of copy
            t2.migrate_taxon_namespace(other_taxon_namespace)

        You can also use this method to get a copy of a structure and then
        move it to a new namespace:

            t2 = Tree(t1)
            t2.migrate_taxon_namespace(TaxonNamespace())

            # Note: the same effect can be achived by:
            t3 = copy.deepcopy(t1)

        See Also
        --------
        reconstruct_taxon_namespace

        """
        if taxon_namespace is None:
            taxon_namespace = taxon.TaxonNamespace()
        self._taxon_namespace = taxon_namespace
        self.reconstruct_taxon_namespace(
                unify_taxa_by_label=unify_taxa_by_label,
                case_sensitive_label_mapping=case_sensitive_label_mapping,
                taxon_mapping_memo=taxon_mapping_memo)

    def reconstruct_taxon_namespace(self,
            unify_taxa_by_label=True,
            case_sensitive_label_mapping=True,
            taxon_mapping_memo=None):
        """
        Repopulates the current taxon namespace with new taxon objects,
        preserving labels. Each distinct :class:`Taxon` object associated with
        `self` or members of `self` that is not already in
        `self.taxon_namespace` will be replaced with a new :class:`Taxon`
        object that will be created with the same label and added to
        :attr:`self.taxon_namespace`.

        Note
        ----
        Existing :class:`Taxon` objects in `self.taxon_namespace` are *not*
        removed. This method should thus only be called *only* when
        `self.taxon_namespace` has been changed. In fact, typical usage would
        not involve calling this method directly, but rather through

        Parameters
        ----------
        unify_taxa_by_label : boolean, optional
            If `True`, then references to distinct :class:`Taxon` objects with
            identical labels in the current namespace will be replaced with a
            reference to a single :class:`Taxon` object in the new namespace.
            If `False`: references to distinct :class:`Taxon` objects will
            remain distinct, even if the labels are the same.

        case_sensitive_label_mapping : boolean, optional
            If `False` and `unify_taxa_by_label` is also `True`, then the
            establishment of correspondence between :class:`Taxon` objects in
            the old and new namespaces with be based on case-insensitive
            matching of labels. E.g., if there are four :class:`Taxon` objects with
            labels 'Foo', 'Foo', 'FOO', and 'FoO' in the old namespace, then
            all objects that reference these will reference a single
            new :class:`Taxon` object in the new namespace (with a label some
            existing casing variant of 'foo'). Defaults to `True`:
            if `unify_taxa_by_label` is `True`, :class:`Taxon` objects with
            labels identical except in case will be considered distinct.

        taxon_mapping_memo : dictionary
            Similar to `memo` of deepcopy, this is a dictionary that maps
            :class:`Taxon` objects in the old namespace to corresponding
            :class:`Taxon` objects in the new namespace. Mostly for interal
            use when migrating complex data to a new namespace.
        """
        raise NotImplementedError()

    def update_taxon_namespace(self):
        """
        All :class:`Taxon` objects associated with `self` or members of `self`
        that are not in `self.taxon_namespace` will be added. Note that, unlike
        :class:`reconstruct_taxon_namespace`, no new :class:`Taxon` objects
        will be created.
        """
        raise NotImplementedError()

    def purge_taxon_namespace(self):
        """
        Remove all :class:`Taxon` instances in `self.taxon_namespace` that are
        not associated with `self` or any item in `self`.
        """
        taxa = self.taxa()
        to_remove = [t for t in self.taxon_namespace if t not in taxa]
        for t in to_remove:
            self.taxon_namespace.remove_taxon(t)

    def taxa(self, taxa=None):
        """
        Returns a set populated with all of :class:`Taxon` instances associated
        with `self`.

        Parameters
        ----------
        taxa : set()
            Set to populate. If not specified, a new one will be created.

        Returns
        -------
        taxa : set[:class:`Taxon`]
            Set of taxa associated with `self`.
        """
        raise NotImplementedError()

    def taxa(self, taxa=None):
        """
        Returns set of :class:`Taxon` instances associated with `self`.

        Parameters
        ----------
        taxa : set()
            Set to populate. If not specified, a new one will be created.

        Returns
        -------
        taxa : set[:class:`Taxon`]
            Set of taxa associated with `self`.
        """
        raise NotImplementedError()

    def reindex_taxa(self, taxon_namespace=None, clear=False):
        """
        DEPRECATED: Use `migrate_taxon_namespace()` instead.
        Rebuilds `taxon_namespace` from scratch, or assigns :class:`Taxon` objects from
        given :class:`TaxonNamespace` object `taxon_namespace` based on label values. Calls
        on `self.reindex_member_taxa()` to synchronize taxa.
        """
        deprecate.dendropy_deprecation_warning(
                message="Deprecated since DendroPy 4: '{class_name}.reindex_taxa()' will no longer be supported in future releases; use '{class_name}.migrate_taxon_namespace()' instead".format(class_name=self.__class__.__name__),
                stacklevel=3)
        if taxon_namespace is not None:
            self.taxon_namespace = taxon_namespace
        if clear:
            self.taxon_namespace.clear()
        self.reindex_subcomponent_taxa()
        return self.taxon_namespace

    def reindex_subcomponent_taxa():
        """
        DEPRECATED: Use :meth:`reconstruct_taxon_namespace()` instead.
        Derived classes should override this to ensure that their various
        components, attributes and members all refer to the same :class:`TaxonNamespace`
        object as `self.taxon_namespace`, and that `self.taxon_namespace` has all
        the :class:`Taxon` objects in the various members.
        """
        raise NotImplementedError()


##############################################################################
## TaxonNamespace

class TaxonNamespace(
        basemodel.DataObject,
        basemodel.Annotable):

    """
    A collection of :class:`Taxon` objects representing a self-contained and complete
    domain of distinct operational taxonomic unit definitions.
    Provides the common semantic context in which operational taxonomic units
    referenced by various phylogenetic data objects (e.g., trees or alignments)
    can be related.
    """

    ### Life-cycle

    def __init__(self, *args, **kwargs):
        """
        Parameters
        ----------

        \*args : positional arguments, optional
            Accepts a single iterable as an optional positional argument.  If a
            :class:`TaxonNamespace` object is passed as the positional argument, then
            clones or deep-copies of its member :class:`Taxon` objects will be added
            to this one.  If any other iterable is passed as the positional
            argument, then each string in the iterable will result in a new
            :class:`Taxon` object being constructed and added to the namespace with
            the string as its label (name), while each Taxon object in the
            iterable will be added to the namespace directly.

        \*\*kwargs : keyword arguments
            label : string
                The label or name for this namespace.
            is_mutable : boolean, optional (default = `True`)
                If `True` (default), then :class:`Taxon` objects can be added to this
                namespace. If `False`, then adding :class:`Taxon` objects will result
                in an error.

        Notes
        -----
        An empty :class:`TaxonNamespace` can be created (with optional) label and :class:`Taxon`
        objects added later:

        >>> tns = dendropy.TaxonNamespace(label="taxa")
        >>> t1 = Taxon("a")
        >>> tns.add_taxon(t1)
        >>> t2 = Taxon("b")
        >>> tns.add_taxon(t2)
        >>> tns.add_taxon("c")
        >>> tns
        <TaxonNamespace 0x106509090 'taxa': [<Taxon 0x10661f050 'a'>, <Taxon 0x10651c590 'b'>, <Taxon 0x106642a90 'c'>]>

        Alternatively, an iterable can be passed in as an initializer, and all
        :class:`Taxon` objects will be added directly while, for each string, a new
        :class:`Taxon` object will be created and added. So, the below are all equivalent
        to the above:

        >>> tns = dendropy.TaxonNamespace(["a", "b", "c"], label="taxa")

        >>> taxa = [Taxon(n) for n in ["a", "b", "c"]]
        >>> tns = dendropy.taxonnamespace(taxa, label="taxa")

        >>> t1 = Taxon("a")
        >>> t2 = Taxon("b")
        >>> taxa = [t1, t2, "c"]
        >>> tns = dendropy.TaxonNamespace(taxa, label="taxa")

        If a :class:`TaxonNamespace` object is passed as the
        initializer argument, a *shallow* copy of the object is constructed:

        >>> tns1 = dendropy.TaxonNamespace(["a", "b", "c"], label="taxa1")
        >>> tns1
        <TaxonNamespace 0x1097275d0 'taxa1': [<Taxon 0x109727610 'a'>, <Taxon 0x109727e10 'b'>, <Taxon 0x109727e90 'c'>]>
        >>> tns2 = dendropy.TaxonNamespace(tns1, label="2")
        >>> tns2
        <TaxonNamespace 0x109727d50 'taxa1': [<Taxon 0x109727610 'a'>, <Taxon 0x109727e10 'b'>, <Taxon 0x109727e90 'c'>]>

        Thus, while "`tns1`" and "`tns2`" are independent collections, and
        addition/deletion of :class:`Taxon` instances to one will not effect
        the other, the label of a :class:`Taxon` instance that is an element in
        one will of course effect the same instance if it is in the other:

        >>> print(tns1[0].label)
        >>> a
        >>> print(tns2[0].label)
        >>> a
        >>> tns1[0].label = "Z"
        >>> print(tns1[0].label)
        >>> Z
        >>> print(tns2[0].label)
        >>> Z

        In contrast to actual data (i.e., the :class:`Taxon` objects), alll
        metadata associated with "`tns2`" (i.e., the :class:`AnnotationSet` object,
        in the :attr:`TaxonNamespace.annotations` attribute), will be a full,
        independent deep-copy.

        If what is needed is a true deep-copy of the data of a particular
        :class:`TaxonNamespace` object, including copies of the member
        :class:`Taxon` instances, then this can be achieved using
        :func:`copy.deepcopy()`.

        >>> import copy
        >>> tns1 = dendropy.TaxonNamespace(["a", "b", "c"], label="taxa1")
        >>> tns2 = copy.deepcopy(tns1)
        """
        kwargs_set_label = kwargs.pop("label", None)
        self.comments = []
        self.is_mutable = kwargs.pop('is_mutable', True)
        self._accession_index_taxon_map = {}
        self._taxa = []
        self._taxon_accession_index_map = {}
        self._taxon_bitmask_map = {}
        # self._split_bitmask_taxon_map = {}
        self._current_accession_count = 0
        if len(args) > 1:
            raise TypeError("TaxonNamespace() takes at most 1 non-keyword argument ({} given)".format(len(args)))
        elif len(args) == 1:
            # special case: construct from argument
            other = args[0]
            for i in other:
                if isinstance(i, Taxon):
                    self.add_taxon(i)
                else:
                    self.new_taxon(label=i)
            if isinstance(other, TaxonNamespace):
                memo = { id(other): self, id(other._taxa): self._taxa }
                for t1, t2 in zip(self._taxa, other._taxa):
                    memo[id(t2)] = t1
                for k in other.__dict__:
                    if k == "_annotations" or k == "_taxa":
                        continue
                    self.__dict__[k] = copy.deepcopy(other.__dict__[k], memo)
                self.deep_copy_annotations_from(other, memo=memo)
                # self.copy_annotations_from(other, attribute_object_mapper=memo)
            # override with label with value passed as argument
            if kwargs_set_label is not None:
                self.label = kwargs_set_label
        else:
            basemodel.DataObject.__init__(self, label=kwargs_set_label)
        if kwargs:
            raise TypeError("Unrecognized or unsupported arguments: {}".format(kwargs))

    def __copy__(self):
        return TaxonNamespace(self)

    def taxon_namespace_scoped_copy(self, memo=None):
        self.populate_memo_for_taxon_namespace_scoped_copy(memo=memo)
        return self

    def __deepcopy__(self, memo):
        if memo is None:
            memo = {}
        o = self.__class__.__new__(self.__class__)
        memo[id(self)] = o
        o._taxa = []
        memo[id(self._taxa)] = o._taxa
        for t in self._taxa:
            o._taxa.append(copy.deepcopy(t, memo))
        for k in self.__dict__:
            if k == "_annotations" or k == "_taxa":
                continue
            o.__dict__[k] = copy.deepcopy(self.__dict__[k], memo)
        o.deep_copy_annotations_from(self, memo=memo)
        # o.copy_annotations_from(self, attribute_object_mapper=memo)
        return o

    def populate_memo_for_taxon_namespace_scoped_copy(self, memo):
        if memo is not None:
            memo[id(self)] = self
            for taxon in self._taxa:
                memo[id(taxon)] = taxon
        return memo

    ### Identity and Comparison

    def __str__(self):
        return "[{}]".format(", ".join([str(i) for i in self._taxa]))

    def __repr__(self):
        return "<{} {} '{}': [{}]>".format(self.__class__.__name__, hex(id(self)), self.label, ", ".join(repr(i) for i in self._taxa))

    def __hash__(self):
        return id(self)

    def __lt__(self, other):
        return self._taxa < o._taxa

    def __eq__(self, other):
        # enforce non-equivalence of non-identical namespaces
        return self is other
        # if not isinstance(other, self.__class__):
        #     return False
        # return (self.label == other.label
        #         and self._taxa == other._taxa
        #         and basemodel.Annotable.__eq__(self, other))

    ### Collection Iteration

    def __iter__(self):
        return iter(self._taxa)

    def __reversed__(self):
        return reversed(self._taxa)

    ### Collection Data

    def __len__(self):
        """
        Returns number of :class:`Taxon` objects in this :class:`TaxonNamespace`.
        """
        return len(self._taxa)

    ### Collection Access and Management

    def __getitem__(self, key):
        """
        Returns :class:`Taxon` object with index or slice given by `key`.
        """
        if isinstance(key, int) or isinstance(key, slice):
            return self._taxa[key]
        raise ValueError("'TaxonNamespace[]' now only accepts indexes or slices. To access Taxon objects by label, use 'TaxonNamespace.get_taxon()' or 'TaxonNamespace.findall()'")

    def __setitem__(self, key, value):
        raise NotImplementedError("Item assignment not supported")

    def __delitem__(self, key):
        self.remove_taxon(self[key])

    def __contains__(self, taxon):
        """
        Returns `True` if Taxon object `taxon` is in self.
        """
        # look-up in dictionary for O(1) instead of O(n) in list
        return taxon in self._taxon_accession_index_map

    ### Adding Taxa

    def add_taxon(self, taxon):
        """
        Adds a new :class:`Taxon` object to `self`.

        If `taxon` is not already in the collection of :class:`Taxon` objects in this
        namespace, and this namespace is mutable, it is added to the
        collection. If it is already in the collection, then nothing happens.
        If it is not already in the collection, but the namespace is not
        mutable, then `TypeError` is raised.

        Parameters
        ----------
        taxon : :class:`Taxon`
            The :class:`Taxon` object to be accessioned or registered in this
            collection.

        Raises
        ------
        TypeError
            If this namespace is immutable (i.e.
            :attr:`TaxonNamespace.is_mutable` is `False`).

        """
        # NOTE
        # Previously, this was:
        #
        #     if taxon in self._taxa:
        #
        # Changing the membership lookup to dictionaries resulted in 10x
        # increase in speed!!!!
        if taxon in self._taxon_accession_index_map:
            return
        if not self.is_mutable:
            raise error.ImmutableTaxonNamespaceError("Taxon '{}' cannot be added to an immutable TaxonNamespace".format((taxon.label)))
        self._taxa.append(taxon)
        self._accession_index_taxon_map[self._current_accession_count] = taxon
        self._taxon_accession_index_map[taxon] = self._current_accession_count
        self._current_accession_count += 1

    def append(self, taxon):
        """
        LEGACY. Use 'add_taxon()' instead.
        """
        return self.add_taxon(taxon)

    def add_taxa(self, taxa):
        """
        Adds multiple :class:`Taxon` objects to self.

        Each :class:`Taxon` object in `taxa` that is not already in the collection of
        :class:`Taxon` objects in this namespace is added to it. If any of the :class:`Taxon`
        objects are already in the collection, then nothing happens. If the
        namespace is immutable, then :class:`TypeError` is raised when trying
        to add :class:`Taxon` objects.

        Parameters
        ----------
        taxa : collections.Iterable [:class:`Taxon`]
            A list of :class:`Taxon` objects to be accessioned or registered in this
            collection.

        Raises
        ------
        TypeError
            If this namespace is immutable (i.e. `TaxonNamespace.is_mutable` is
            `False`).
        """
        for t in taxa:
            self.add_taxon(t)

    def new_taxon(self, label):
        """
        Creates, adds, and returns a new :class:`Taxon` object with corresponding
        label.

        Parameters
        ----------
        label : string or string-like
            The name or label of the new operational taxonomic unit concept.

        Returns
        -------
        taxon: :class:`Taxon`
            The new :class:`Taxon` object,

        """
        if not self.is_mutable:
            raise error.ImmutableTaxonNamespaceError("Taxon '{}' cannot be added to an immutable TaxonNamespace".format(label))
        taxon = Taxon(label=label)
        self.add_taxon(taxon)
        return taxon

    def new_taxa(self, labels):
        """
        Creates and add a new :class:`Taxon` with corresponding label for each label
        in `labels`. Returns list of :class:`Taxon` objects created.

        Parameters
        ----------
        labels : :py:class:`collections.Iterable` [string]
            The values of the `label` attributes of the new :class:`Taxon` objects to
            be created, added to this namespace collection, and returned.

        Returns
        -------
        taxa : :py:class:`collections.Iterable` [:class:`Taxon`]
            A list of :class:`Taxon` objects created and added.

        Raises
        ------
        TypeError
            If this namespace is immutable (i.e. `TaxonNamespace.is_mutable` is
            `False`).

        """
        if not self.is_mutable:
            raise error.ImmutableTaxonNamespaceError("Taxon objects cannot be added to an immutable TaxonNamespace")
        taxa = []
        for label in labels:
            taxa.append(self.new_taxon(label=label))
        return taxa

    ### Removing Taxa

    def remove_taxon(self, taxon):
        """
        Removes specified :class:`Taxon` object from the collection in this namespace.

        Parameters
        ----------
        taxon : a :class:`Taxon` object
            The :class:`Taxon` object to be removed.

        Raises
        ------
        ValueError
            If `taxon` is not in the collection of this namespace.
        """
        if taxon not in self._taxa:
            raise ValueError(taxon)
        self._taxa.remove(taxon)
        # assert taxon not in self._taxa
        while taxon in self._taxa:
            self._taxa.remove(taxon)
        idx = self._taxon_accession_index_map.pop(taxon, None)
        if idx is not None:
            self._accession_index_taxon_map.pop(idx, None)
            self._taxon_accession_index_map.pop(taxon, None)
        bm = self._taxon_bitmask_map.pop(taxon, None)
        if bm is not None:
            # self._split_bitmask_taxon_map.pop(bm, None)
            self._taxon_accession_index_map.pop(taxon, None)

    def remove_taxon_label(self, label, case_sensitive=False):
        """
        Removes *all* :class:`Taxon` objects with label matching `label` from the
        collection in this namespace.

        Parameters
        ----------
        label : string or string-like
            The value of the :class:`Taxon` object label to remove.
        case_sensitive : boolean, optional
            If `True`, then the label matching is done as-is. If `False`
            (default), then both the `label` argument as well as the
            :class:`Taxon` object's `label` attribute are coerced into
            lower-case label strings before checking for a match.

        Raises
        ------
        LookupError
            If no :class:`Taxon` objects are found with matching label(s).

        See Also
        --------
        :meth:`TaxonNamespace.discard_taxon_labels`
            Similar, but does not raise an error if no matching :class:`Taxon`
            objects are found.
        """
        taxa = self._lookup_label(label,
                case_sensitive=case_sensitive,
                multiple=True,
                error_if_not_found=True)
        for taxon in taxa:
            self.remove_taxon(taxon)

    def discard_taxon_label(self, label, case_sensitive=False):
        """
        Removes *all* :class:`Taxon` objects with label matching `label` from the
        collection in this namespace.

        Parameters
        ----------
        label : string or string-like
            The value of the :class:`Taxon` object label to remove.
        case_sensitive : boolean, optional
            If `True`, then the label matching is done as-is. If `False`
            (default), then both the `label` argument as well as the
            :class:`Taxon` object's `label` attribute are coerced into
            lower-case label strings before checking for a match.

        See Also
        --------
        :meth:`TaxonNamespace.discard_taxon_labels` : Similar, but does not
            raise an error if no matching :class:`Taxon` objects are found.
        """
        taxa = self._lookup_label(label,
                case_sensitive=case_sensitive,
                multiple=True,
                error_if_not_found=False)
        if taxa is None:
            return
        for taxon in taxa:
            self.remove_taxon(taxon)

    def clear(self):
        """
        Removes all :class:`Taxon` objects from this namespace.
        """
        # self._taxa.clear() # Python 2 `list` class does not have `clear()` method
        del self._taxa[:]
        self._accession_index_taxon_map.clear()
        self._taxon_accession_index_map.clear()
        self._taxon_bitmask_map.clear()
        # self._split_bitmask_taxon_map.clear()

    ### Look-up and Retrieval of Taxa

    def _lookup_label(self,
            label,
            multiple=True,
            case_sensitive=False,
            error_if_not_found=False):
        """
        Return :class:`Taxon` object(s) with label matching `label`.
        If `multiple` is `True`, then a list of :class:`Taxon` objects with labels
        that match `label` are returned, otherwise just the first one is
        returned. If `case_sensitive` is `False`, then the matching is done
        without regard for case. If no :class:`Taxon` object is in the current the
        namespace that matches the criteria, then `None` is returned unless
        `error_if_not_found` is `False`, in which case :class:`LookupError` is raised.
        """
        taxa = []
        if not case_sensitive:
            label = str(label).lower()
            for taxon in self._taxa:
                if label == str(taxon.label).lower():
                    if not multiple:
                        return taxon
                    else:
                        taxa.append(taxon)
        else:
            for taxon in self._taxa:
                if label == taxon.label:
                    if not multiple:
                        return taxon
                    else:
                        taxa.append(taxon)
        if len(taxa) > 0:
            return taxa
        elif error_if_not_found:
            raise LookupError(label)
        else:
            return None

    def findall(self, label, case_sensitive=False):
        """
        Return list of :class:`Taxon` object(s) with label matching `label`.

        Parameters
        ----------
        label : string or string-like
            The value which the `label` attribute of the :class:`Taxon` object(s)
            to be returned must match.
        case_sensitive : boolean, optional
            If `True`, then the label matching is done as-is. If `False`
            (default), then both the `label` argument as well as the
            :class:`Taxon` object's `label` attribute are coerced into
            lower-case label strings before checking for a match.

        Returns
        -------
        taxa : :py:class:`list` [:class:`Taxon`]
            A list containing zero or more :class:`Taxon` objects with labels
            matching `label`.

        Raises
        ------
        TypeError
            If this namespace is immutable (i.e. `TaxonNamespace.is_mutable` is
            `False`).

        """
        taxa = self._lookup_label(
                label=label,
                multiple=True,
                case_sensitive=case_sensitive,
                error_if_not_found=False)
        if taxa is None:
            return []
        else:
            return taxa

    def has_taxon_label(self, label, case_sensitive=False):
        """
        Checks for presence of a :class:`Taxon` object with the given label.

        Parameters
        ----------
        label : string or string-like
            The value of the :class:`Taxon` object label to match.
        case_sensitive : boolean, optional
            If `True`, then the label matching is done as-is. If `False`
            (default), then both the `label` argument as well as the
            :class:`Taxon` object's `label` attribute are coerced into
            lower-case label strings before checking for a match.

        Returns
        -------
        b : boolean
            `True` if there is at least one :class:`Taxon` object in this namespace
            with a label matching the value of `label`. Otherwise, `False`.
        """
        t = self._lookup_label(
                label=label,
                multiple=False,
                case_sensitive=case_sensitive,
                error_if_not_found=False)
        return t is not None

    def has_taxa_labels(self, labels, case_sensitive=False):
        """
        Checks for presence of :class:`Taxon` objects with the given labels.

        Parameters
        ----------
        labels : :py:class:`collections.Iterable` [string]
            The values of the :class:`Taxon` object labels to match.
        case_sensitive : boolean, optional
            If `True`, then the label matching is done as-is. If `False`
            (default), then both the `label` argument as well as the
            :class:`Taxon` object's `label` attribute are coerced into
            lower-case label strings before checking for a match.

        Returns
        -------
        b : boolean
            Returns `True` if, for every element in the iterable `labels`,
            there is at least one :class:`Taxon` object that has a label attribute
            that matches this. `False` otherwise.
        """
        for label in labels:
            f = self._lookup_label(label=label,
                    multiple=False,
                    case_sensitive=case_sensitive,
                    error_if_not_found=False)
            if f is None:
                return False
        return True

    def get_taxon(self, label, case_sensitive=False):
        """
        Retrieves a :class:`Taxon` object with the given label.

        If `casine_sensitive` is `False`, then the label matching is made
        without regard for case.  If multiple :class:`Taxon` objects exist with labels
        that match `label`, then only the first one is returned.  If no :class:`Taxon`
        object is found in this namespace with the specified critieria, `None`
        is returned.

        Parameters
        ----------
        label : string or string-like
            The value which the `label` attribute of the :class:`Taxon` object
            to be returned must match.
        case_sensitive : boolean,
            If `True`, then the label matching is done as-is. If `False`
            (default), then both the `label` argument as well as the
            :class:`Taxon` object's `label` attribute are coerced into
            lower-case label strings before checking for a match.

        Returns
        -------
        taxon : :class:`Taxon` object or `None`
            The first :class:`Taxon` object in this namespace collection with a label
            matching `label`, or `None` if no such :class:`Taxon` object exists.
        """
        return self._lookup_label(label=label,
                multiple=False,
                case_sensitive=case_sensitive,
                error_if_not_found=False)

    def get_taxa(self, labels, case_sensitive=False):
        """
        Retrieves list of :class:`Taxon` objects with given labels.

        If `case_sensitive` is `True`, then the label matching is made
        without regard for case.

        Parameters
        ----------
        labels : :py:class:`collections.Iterable` [string]
            Any :class:`Taxon` object in this namespace collection that has a label
            attribute that matches any value in `labels` will be included in
            the list returned.
        case_sensitive : boolean, optional
            If `True`, then the label matching is done as-is. If `False`
            (default), then both the `label` argument as well as the
            :class:`Taxon` object's `label` attribute are coerced into
            lower-case label strings before checking for a match.

        Returns
        -------
        taxa : :py:class:`list` [:class:`Taxon`]
            A list containing zero or more :class:`Taxon` objects with labels
            matching `label`.
        """
        taxa = []
        for label in labels:
            tt = self._lookup_label(label=label,
                    multiple=True,
                    case_sensitive=case_sensitive,
                    error_if_not_found=False)
            if tt is None:
                continue
            for t in tt:
                if t not in taxa:
                    taxa.append(t)
        return taxa

    def require_taxon(self, label, case_sensitive=False):
        """
        Retrieves a :class:`Taxon` object with the given label, creating it if
        necessary.

        Retrieves a Taxon object with the label, `label`.  If `case_sensitive`
        is `False`, then the label matching is made without regard for case.
        If multiple :class:`Taxon` objects exist with labels that match
        `label`, then only the first one is returned.  If no such
        :class:`Taxon` object exists in the current namespace and the
        :class:`TaxonNamespace` is NOT mutable, an exception is raised.  If no
        such :class:`Taxon` object exists in the current namespace and
        :class:`TaxonNamespace` is mutable, then a new :class:`Taxon` is
        created, added, and returned.

        Parameters
        ----------
        label : string or string-like
            The value which the `label` attribute of the :class:`Taxon` object
            to be returned must match.
        case_sensitive : boolean, optional
            If `True`, then the label matching is done as-is. If `False`
            (default), then both the `label` argument as well as the
            :class:`Taxon` object's `label` attribute are coerced into
            lower-case label strings before checking for a match.

        Returns
        -------
        taxon : :class:`Taxon` object or `None`
            A :class:`Taxon` object in this namespace collection with a label
            matching `label`.

        Raises
        ------
        TypeError
            If no :class:`Taxon` object is currently in the collection with a label
            matching the input `label` and the `is_mutable` attribute of self
            is `False`.
        """
        taxon = self._lookup_label(label=label,
                multiple=False,
                case_sensitive=case_sensitive,
                error_if_not_found=False)
        if taxon is not None:
            return taxon
        if not self.is_mutable:
            raise error.ImmutableTaxonNamespaceError("Taxon '{}' not in TaxonNamespace, and cannot be created because TaxonNamespace is immutable".format(label))
        taxon = self.new_taxon(label=label)
        return taxon

    ### Taxon Ordering

    def sort(self, key=None, reverse=False):
        """
        Sorts :class:`Taxon` objects in collection. If `key` is not given, defaults
        to sorting by label (i.e., `key = lambda x: x.label`).

        Parameters
        ----------
        key : key function object, optional
            Function that takes a :class:`Taxon` object as an argument and
            returns the value that determines its sort order. Defaults to
            sorting by label.
        reverse : boolean, optional
            If `True`, sort will be in reverse order.
        """
        if key is None:
            key = lambda x: x.label
        self._taxa.sort(key=key, reverse=reverse)

    def reverse(self):
        """
        Reverses order of :class:`Taxon` objects in collection.
        """
        self._taxa.reverse()

    ### Summarization of Collection

    def labels(self):
        """
        Returns list of labels of all :class:`Taxon` objects in `self`.

        Returns
        -------
        labels : :py:class:`list` [string]
            List of :attr:`Taxon.label` values of :class:`Taxon` objects in
            `self`.
        """
        return [t.label for t in self._taxa]

    def label_taxon_map(self, case_sensitive_keys=False):
        """
        Returns dictionary with taxon labels as keys and corresponding :class:`Taxon`
        objects as values.

        No attempt is made to handle collisions.

        Parameters
        ----------
        case_sensitive_keys : boolean, optional
            If `True` (default), then normal Python `dict` object will be
            returned, resulting in case-sensitive keys. If `False`, then a
            :class:`CaseInsensitiveDict` object will return, allowing for
            case-insensitive lookups.

        Returns
        -------
        d : :py:class:`dict` or :class:`CaseInsensitiveDict`
            Dictionary with :attr:`Taxon.label` values of :class:`Taxon` objects in
            `self` as keys and corresponding :class:`Taxon` objects as values.
        """
        if not case_sensitive_keys:
            d = container.CaseInsensitiveDict()
        else:
            d = {}
        for t in self._taxa:
            d[t.label] = t
        return d

    ### Split Management

    # def complement_bitmask(self, bitmask):
    #     """
    #     Returns complement of the given split or clade bitmask.

    #     Parameters
    #     ----------
    #     bitmask : integer
    #         Bitmask to be complemented.

    #     Returns
    #     -------
    #     h : integer
    #         Complement of `bitmask`.
    #     """
    #     return (~bitmask) & self.all_taxa_bitmask()

    # def normalize_bitmask(self, bitmask):
    #     """
    #     "Normalizes" split, by ensuring that the least-significant bit is
    #     always 1 (used on unrooted trees to establish split identity
    #     independent of rotation).

    #     Parameters
    #     ----------
    #     bitmask : integer
    #         Split bitmask hash to be normalized.

    #     Returns
    #     -------
    #     h : integer
    #         Normalized split bitmask.
    #     """
    #     return container.NormalizedBitmaskDict.normalize(bitmask, self.all_taxa_bitmask(), 1)

    def all_taxa_bitmask(self):
        """
        Returns mask of all taxa.

        Returns
        -------
        h : integer
            Bitmask spanning all :class:`Taxon` objects in self.
        """
        #return pow(2, len(self)) - 1
        b = 1 << self._current_accession_count
        return b - 1

    def taxon_bitmask(self, taxon):
        """
        Returns bitmask value of split hash for split subtending node with
        `taxon`.

        Parameters
        ----------
        taxon : :class:`Taxon`
            :class:`Taxon` object for which to calculate split hash bitmask.

        Returns
        -------
        h : integer
            Split hash bitmask value for node associated with :class:`Taxon` object `taxon`.
        """
        # i = self._taxa.index(taxon)
        # m = 1 << i
        # return m
        try:
            return self._taxon_bitmask_map[taxon]
        except KeyError:
            i = self._taxon_accession_index_map[taxon]
            # i = self._taxa.index(taxon)
            m = 1 << i
            self._taxon_bitmask_map[taxon] = m
            # self._split_bitmask_taxon_map[m] = taxon
            return m

    def accession_index(self, taxon):
        """
        Returns the accession index of `taxon`. Note that this may not be the
        same as the list index of the taxon if taxa have been deleted from the
        namespace.

        Parameters
        ----------
        taxon : :class:`Taxon`
            :class:`Taxon` object for which to return the accession index.

        Returns
        -------
        h : integer
            The accession index.
        """
        return self._taxon_accession_index_map[taxon]

    def taxa_bitmask(self, **kwargs):
        """
        Retrieves the list of split hash bitmask values representing all taxa
        specified by keyword-specified list of taxon objects (`taxa=`) or
        labels (`labels=`).

        Parameters
        ----------
        \*\*kwargs : keyword arguments
            Requires one of:

                taxa : :py:class:`collections.Iterable` [:class:`Taxon`]
                    Iterable of :class:`Taxon` objects.
                labels : :py:class:`collections.Iterable` [string]
                    Iterable of :class:`Taxon` label values.

        Returns
        -------
        b : :py:class:`list` [integer]
            List of split hash bitmask values for specified :class:`Taxon`
            objects.
        """
        if "taxa" in kwargs:
            taxa = kwargs["taxa"]
        else:
            taxa = self.get_taxa(**kwargs)
        bitmask = 0
        for taxon in taxa:
            bitmask |= self.taxon_bitmask(taxon)
        return bitmask

    def get_taxa_bitmask(self, **kwargs):
        """
        LEGACY. Use 'taxa_bitmask' instead.
        """
        return self.taxa_bitmask(**kwargs)

    def bitmask_taxa_list(self, bitmask, index=0):
        """
        Returns list of :class:`Taxon` objects represented by split
        `bitmask`.

        Parameters
        ----------
        bitmask : integer
            Split hash bitmask value.
        index : integer, optional
            Start from this :class:`Taxon` object instead of the first
            :class:`Taxon` object in the collection.

        Returns
        -------
        taxa : :py:class:`list` [:class:`Taxon`]
            List of :class:`Taxon` objects specified or spanned by
            `bitmask`.
        """
        taxa = []
        while bitmask:
            if bitmask & 1:
                taxa.append(self._accession_index_taxon_map[index])
            bitmask = bitmask >> 1
            index += 1
        return taxa

    def bitmask_as_newick_string(self,
            bitmask,
            preserve_spaces=False,
            quote_underscores=True):
        """
        Represents a split as a newick string.

        Parameters
        ----------
        bitmask : integer
            Split hash bitmask value.
        preserve_spaces : boolean, optional
            If `False` (default), then spaces in taxon labels will be replaced
            by underscores. If `True`, then taxon labels with spaces will be
            wrapped in quotes.
        quote_underscores : boolean, optional
            If `True` (default), then taxon labels with underscores will be
            wrapped in quotes. If `False`, then the labels will not be wrapped
            in quotes.

        Returns
        -------
        s : string
            NEWICK representation of split specified by `bitmask`.
        """
        from dendropy.dataio import nexusprocessing
        return nexusprocessing.bitmask_as_newick_string(
                bitmask,
                self,
                preserve_spaces=preserve_spaces,
                quote_underscores=quote_underscores)

    def bitmask_as_bitstring(self, b):
        return bitprocessing.int_as_bitstring(b, length=self._current_accession_count)

    def description(self, depth=1, indent=0, itemize="", output=None, **kwargs):
        """
        Returns description of object, up to level `depth`.
        """
        if depth is None or depth < 0:
            return ""
        output_strio = StringIO()
        if self.label is None:
            label = str(self.label)
        output_strio.write('%s%sTaxonNamespace object at %s%s'
                % (indent*' ',
                   itemize,
                   hex(id(self)),
                   label))
        if depth >= 1:
            output_strio.write(': %d Taxa' % len(self))
            if depth >= 2 and len(self) > 0:
                for i, t in enumerate(self):
                    output_strio.write('\n')
                    t.description(depth=depth-1, indent=indent+4, itemize="[%d]" % (i), output=output_strio, **kwargs)
        s = output_strio.getvalue()
        if output is not None:
            output.write(s)
        return s

##############################################################################
## TaxonSet

class TaxonSet(TaxonNamespace):
    """
    This class is present for (temporary!) legacy support of code written under
    DendroPy 3.x.  It will be removed in future versions. All new code should
    be written using :class:`TaxonNamespace`. Old code needs to be updated to use
    :class:`TaxonNamespace`.
    """

    def __init__(self, *args, **kwargs):
        deprecate.dendropy_deprecation_warning(
                message="Deprecated since DendroPy 4: 'TaxonSet' will no longer be supported in future releases; use 'TaxonNamespace' instead",
                stacklevel=3)
        TaxonNamespace.__init__(self, *args, **kwargs)

##############################################################################
## Taxon

class Taxon(
        basemodel.DataObject,
        basemodel.Annotable):
    """
    A taxon associated with a sequence or a node on a tree.
    """

    def __init__(self, label=None):
        """
        Parameters
        ----------
        label : string or :class:`Taxon` object
            Label or name of this operational taxonomic unit concept. If a
            string, then the `label` attribute of `self` is set to this value.
            If a :class:`Taxon` object, then the `label` attribute of `self` is
            set to the same value as the `label` attribute the other
            :class:`Taxon` object and all annotations/metadata are copied.
        """
        if isinstance(label, Taxon):
            other_taxon = label
            label = other_taxon.label
            memo={id(other_taxon):self}
            for k in other_taxon.__dict__:
                if k != "_annotations":
                    self.__dict__[k] = copy.deepcopy(other_taxon.__dict__[k], memo=memo)
            self.deep_copy_annotations_from(other_taxon, memo=memo)
            # self.copy_annotations_from(other_taxon, attribute_object_mapper=memo)
        else:
            basemodel.DataObject.__init__(self, label=label)
        self.comments = []

    def __copy__(self):
        raise TypeError("Cannot shallow-copy Taxon")
        # return self

    def taxon_namespace_scoped_copy(self, memo=None):
        if memo is not None:
            memo[id(self)] = self
        return self

    def __deepcopy__(self, memo=None):
        if memo is None:
            memo = {}
        try:
            o = memo[id(self)]
        except KeyError:
            # o = type(self).__new__(self.__class__)
            o = self.__class__.__new__(self.__class__)
            memo[id(self)] = o
        for k in self.__dict__:
            if k != "_annotations":
                o.__dict__[k] = copy.deepcopy(self.__dict__[k], memo)
        o.deep_copy_annotations_from(self, memo)
        # o.copy_annotations_from(self, attribute_object_mapper=memo)
        return o

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self is other

    def __lt__(self, other):
        return self.label < other.label

    def __str__(self):
        "String representation of self = taxon name."
        return "'{}'".format(self._label)

    def __repr__(self):
        return "<{} {} '{}'>".format(self.__class__.__name__, hex(id(self)), self._label)

    def description(self, depth=1, indent=0, itemize="", output=None, **kwargs):
        """
        Returns description of object, up to level `depth`.
        """
        if depth is None or depth < 0:
            return ""
        output_strio = StringIO()
        if self._label is None:
            label = "<Unnamed Taxon>"
        else:
            label = "'{}'".format(self._label)
        output_strio.write('{}{} Taxon object at {}: {}'.format(indent*' ', itemize, hex(id(self)), label))
        s = output_strio.getvalue()
        if output is not None:
            output.write(s)
        return s

##############################################################################
## TaxonNamespacePartition

class TaxonNamespacePartition(TaxonNamespaceAssociated):
    """
    Manages a partition of a TaxonNamespace (i.e., a set of mutually-exclusive
    and exhaustive subsets of a TaxonNamespace).
    """

    def __init__(self, taxon_namespace, **kwargs):
        """
        __init__ uses one of the following keyword arguments:

            - `membership_func`
                A function that takes a ``Taxon`` object as an argument and
                returns a a population membership identifier or flag
                (e.g., a string, an integer) .
            - `membership_attr_name`
                Name of an attribute of ``Taxon`` objects that serves as an
                identifier for subset membership.
            - `membership_dict`
                A dictionary with ``Taxon`` objects as keys and population
                membership identifier or flag as values (e.g., a string,
                an integer).
            - `membership_lists`
                A container of containers of ``Taxon`` objects, with every
                ``Taxon`` object in ``taxon_namespace`` represented once and only
                once in the sub-containers.

        If none of these are specified, defaults to a partition consisting of
        a single subset with all the objects in ``taxon_namespace``.
        """
        TaxonNamespaceAssociated.__init__(self,
                taxon_namespace=taxon_namespace)
        self.subset_map = {}
        if taxon_namespace is not None:
            if len(kwargs) > 0:
                self.apply(**kwargs)
            else:
                ss = TaxonNamespace(self.taxon_namespace)
                self.subset_map = { self.taxon_namespace.label : ss}

    def subsets(self):
        """
        Return subsets of partition.
        """
        return set(self.subset_map.values())

    def __len__(self):
        """
        Number of subsets.
        """
        return len(self.subset_map)

    def __iter__(self):
        """
        Iterate over subsets.
        """
        for k, v in self.subset_map.items():
            yield v

    def __getitem__(self, label):
        """
        Get subset with specified label.
        """
        return self.subset_map[label]

    def apply(self, **kwargs):
        """
        Builds the subsets of the linked TaxonNamespace resulting from the
        partitioning scheme specified by one of the following keyword arguments:

            ``membership_func``
                A function that takes a ``Taxon`` object as an argument and
                returns a a population membership identifier or flag
                (e.g., a string, an integer).

            ``membership_attr_name``
                Name of an attribute of ``Taxon`` objects that serves as an
                identifier for subset membership.

            ``membership_dict``
                A dictionary with ``Taxon`` objects as keys and population
                membership identifier or flag as values (e.g., a string,
                an integer).

            ``membership_lists``
                A container of containers of ``Taxon`` objects, with every
                ``Taxon`` object in ``taxon_namespace`` represented once and only
                once in the sub-containers.
        """
        if "membership_func" in kwargs:
            self.apply_membership_func(kwargs["membership_func"])
        elif  "membership_attr_name" in kwargs:
            self.apply_membership_attr_name(kwargs["membership_attr_name"])
        elif  "membership_dict" in kwargs:
            self.apply_membership_dict(kwargs["membership_dict"])
        elif "membership_lists" in kwargs:
            self.apply_membership_lists(kwargs["membership_lists"])
        else:
            raise TypeError("Must specify partitioning scheme using one of: " \
                + "'membership_func', 'membership_dict', or 'membership_lists'")

    def apply_membership_func(self, mfunc):
        """
        Constructs subsets based on function ``mfunc``, which should take a
        ``Taxon`` object as an argument and return a population membership
        identifier or flag (e.g., a string, an integer).
        """
        self.subset_map = {}
        for t in self.taxon_namespace:
            subset_id = mfunc(t)
            if subset_id not in self.subset_map:
                self.subset_map[subset_id] = TaxonNamespace(label=subset_id)
            self.subset_map[subset_id].add_taxon(t)
        return self.subsets()

    def apply_membership_attr_name(self, attr_name):
        """
        Constructs subsets based on attribute ``attr_name`` of each
        ``Taxon`` object.
        """
        return self.apply_membership_func(lambda x: getattr(x, attr_name))

    def apply_membership_dict(self, mdict):
        """
        Constructs subsets based on dictionary ``mdict``, which should be
        dictionary with ``Taxon`` objects as keys and population membership
        identifier or flag as values (e.g., a string, an integer).
        """
        return self.apply_membership_func(lambda x: mdict[x])

    def apply_membership_lists(self, mlists, subset_labels=None):
        """
        Constructs subsets based on list ``mlists``, which should be an interable
        of iterables of ``Taxon`` objects, with every ``Taxon`` object in
        ``taxon_namespace`` represented once and only once in the sub-containers.
        """
        if subset_labels is not None:
            if len(subset_labels) != len(mlists):
                raise ValueError('Length of subset label list must equal to number of subsets')
        else:
            subset_labels = range(len(mlists))
        self.subset_map = {}
        for lidx, mlist in enumerate(mlists):
            subset_id = subset_labels[lidx]
            self.subset_map[subset_id] = TaxonNamespace(label=subset_id)
            for i, t in enumerate(mlist):
                self.subset_map[subset_id].add_taxon(t)
        return self.subsets()

##############################################################################
## TaxonNamespaceMapping

class TaxonNamespaceMapping(
        basemodel.DataObject,
        basemodel.Annotable):
    """
    A many-to-one mapping of ``Taxon`` objects (e.g., gene taxa to population/species taxa).
    """

    @staticmethod
    def create_contained_taxon_mapping(containing_taxon_namespace,
            num_contained,
            contained_taxon_label_prefix=None,
            contained_taxon_label_separator=' ',
            contained_taxon_label_func=None):
        """
        Creates and returns a TaxonNamespaceMapping object that maps multiple
        "contained" Taxon objects (e.g., genes) to Taxon objects in
        `containing_taxon_namespace` (e.g., populations or species).

            `containing_taxon_namespace`
                A TaxonNamespace object that defines a Taxon for each population or
                species.

            `num_contained`
                The number of genes per population of species. The value of
                this attribute can be a scalar integer, in which case each
                species or population taxon will get the same fixed number
                of genes. Or it can be a list, in which case the list has
                to have as many elements as there are members in
                `containing_taxon_namespace`, and each element will specify the
                number of genes that the corresponding species or population
                Taxon will get.

            `contained_taxon_label_prefix`
                If specified, then each gene Taxon label will begin with this.
                Otherwise, each gene Taxon label will begin with the same label
                as its corresponding species/population taxon label.

            `contained_taxon_label_separator`
                String used to separate gene Taxon label prefix from its index.

            `contained_taxon_label_func`
                If specified, should be a function that takes two arguments: a
                Taxon object from `containing_taxon_namespace` and an integer
                specifying the contained gene index. It should return a string
                which will be used as the label for the corresponding gene
                taxon. If not None, this will bypass the
                `contained_taxon_label_prefix` and
                `contained_taxon_label_separator` arguments.
        """
        if isinstance(num_contained, int):
            _num_contained = [num_contained] * len(containing_taxon_namespace)
        else:
            _num_contained = num_contained
        contained_to_containing = {}
        contained_taxa = TaxonNamespace()
        for cidx, containing_taxon in enumerate(containing_taxon_namespace):
            num_new = _num_contained[cidx]
            for new_idx in range(num_new):

                if contained_taxon_label_func is not None:
                    label = contained_taxon_label_func(containing_taxon,
                            new_idx)
                else:
                    label = "%s%s%d" % (containing_taxon.label,
                            contained_taxon_label_separator,
                            new_idx+1)
                contained_taxon = Taxon(label=label)
                contained_to_containing[contained_taxon] = containing_taxon
                contained_taxa.append(contained_taxon)
        contained_to_containing_map = TaxonNamespaceMapping(domain_taxon_namespace=contained_taxa,
                range_taxon_namespace=containing_taxon_namespace,
                mapping_dict=contained_to_containing)
        return contained_to_containing_map

    def __init__(self, **kwargs):
        """
        __init__ uses one of the following keyword arguments:

            - `mapping_func`
                A function that takes a ``Taxon`` object from the domain taxa
                as an argument and returns the corresponding ``Taxon`` object
                from the range taxa. If this argument is given, then a
                ``TaxonNamespace`` or some other container of ``Taxon`` objects needs
                to be passed using the ``taxon_namespace`` argument.
            - `mapping_attr_name`
                Name of an attribute of ``Taxon`` object of the domain taxa
                that references the corresponding ``Taxon`` object from the
                range taxa. If this argument is given, then a ``TaxonNamespace`` or
                some other container of ``Taxon`` objects needs to be passed
                using the ``taxon_namespace`` argument.
            - `mapping_dict`
                A dictionary with ``Taxon`` objects from the domain taxa as
                keys, and the corresponding ``Taxon`` object from the range
                taxa as values.
        """
        basemodel.DataObject.__init__(self, label=kwargs.pop("label", None))
        self.forward = {}
        self.reverse = {}
        if "mapping_func" in kwargs:
            if "domain_taxon_namespace" not in kwargs:
                raise TypeError("Must specify 'domain_taxon_namespace'")
            self.apply_mapping_func(kwargs["mapping_func"],
                    domain_taxon_namespace=kwargs["domain_taxon_namespace"],
                    range_taxon_namespace=kwargs.get("range_taxon_namespace", None))
        elif "mapping_attr_name" in kwargs:
            if "domain_taxon_namespace" not in kwargs:
                raise TypeError("Must specify 'domain_taxon_namespace'")
            self.apply_mapping_attr_name(kwargs["mapping_attr_name"],
                    domain_taxon_namespace=kwargs["domain_taxon_namespace"],
                    range_taxon_namespace=kwargs.get("range_taxon_namespace", None))
        elif "mapping_dict" in kwargs:
            self.apply_mapping_dict(kwargs["mapping_dict"],
                    domain_taxon_namespace=kwargs.get("domain_taxon_namespace", None),
                    range_taxon_namespace=kwargs.get("range_taxon_namespace", None))
        else:
            raise TypeError("Must specify at least one of: 'mapping_func', 'mapping_attr_name', or 'mapping_dict'")

    def __len__(self):
        """
        Number of subsets.
        """
        return len(self.forward)

    def __iter__(self):
        """
        Iterate over subsets.
        """
        for k in self.forward:
            yield k

    def items(self):
        return self.forward.items()

    def keys(self):
        return self.forward.keys()

    def __getitem__(self, taxon):
        """
        Get mapping for specified taxon.
        """
        return self.forward[taxon]

    def _get_domain_taxon_namespace(self):
        return self._domain_taxon_namespace

    def _set_domain_taxon_namespace(self, taxa):
        if taxa and not isinstance(taxa, TaxonNamespace):
            self._domain_taxon_namespace = TaxonNamespace(taxa)
        else:
            self._domain_taxon_namespace = taxa

    domain_taxon_namespace = property(_get_domain_taxon_namespace, _set_domain_taxon_namespace)

    def _get_range_taxon_namespace(self):
        return self._range_taxon_namespace

    def _set_range_taxon_namespace(self, taxa):
        if taxa and not isinstance(taxa, TaxonNamespace):
            self._range_taxon_namespace = TaxonNamespace(taxa)
        else:
            self._range_taxon_namespace = taxa

    range_taxon_namespace = property(_get_range_taxon_namespace, _set_range_taxon_namespace)

    def apply_mapping_func(self, mfunc, domain_taxon_namespace, range_taxon_namespace=None):
        """
        Constructs forward and reverse mapping dictionaries based on ``mfunc``,
        which should take a ``Taxon`` object in ``domain_taxon_namespace`` as an argument
        and return another ``Taxon`` object.
        """
        self.forward = {}
        self.reverse = {}
        self.domain_taxon_namespace = domain_taxon_namespace
        if range_taxon_namespace is None:
            self.range_taxon_namespace = TaxonNamespace()
        else:
            self.range_taxon_namespace = range_taxon_namespace
        for dt in self.domain_taxon_namespace:
            rt = mfunc(dt)
            if rt not in self.range_taxon_namespace:
                self.range_taxon_namespace.add_taxon(rt)
            self.forward[dt] = rt
            try:
                self.reverse[rt].add(dt)
            except KeyError:
                self.reverse[rt] = set([dt])

    def apply_mapping_attr_name(self, attr_name, domain_taxon_namespace, range_taxon_namespace=None):
        """
        Constructs mapping based on attribute ``attr_name`` of each
        ``Taxon`` object in ``domain_taxon_namespace``.
        """
        return self.apply_mapping_func(lambda x: getattr(x, attr_name), domain_taxon_namespace=domain_taxon_namespace, range_taxon_namespace=range_taxon_namespace)

    def apply_mapping_dict(self, mdict, domain_taxon_namespace=None, range_taxon_namespace=None):
        """
        Constructs mapping based on dictionary ``mdict``, which should have
        domain taxa as keys and range taxa as values.
        """
        if domain_taxon_namespace is None:
            domain_taxon_namespace = TaxonNamespace(mdict.keys())
        return self.apply_mapping_func(lambda x: mdict[x], domain_taxon_namespace=domain_taxon_namespace, range_taxon_namespace=range_taxon_namespace)

    def mesquite_association_rows(self):
        from dendropy.dataio import nexusprocessing
        rows = []
        for rt in self.reverse:
            x1 = nexusprocessing.escape_nexus_token(rt.label)
            dt_labels = [dt.label for dt in self.reverse[rt]]
            dt_labels.sort()
            x2 = " ".join([nexusprocessing.escape_nexus_token(d) for d in dt_labels])
            rows.append("        %s / %s" % (x1, x2))
        return ",\n".join(rows)

    def write_mesquite_association_block(self, out, domain_taxon_namespace_title=None, range_taxon_namespace_title=None):
        """
        For debugging purposes ...
        """
        def _compose_title(b):
            if b.label:
                return b.label
            else:
                return "d{}".format(id(b))
        from dendropy.dataio import nexusprocessing
        out.write("BEGIN TaxaAssociation;\n")
        title = _compose_title(self)
        out.write("    TITLE %s;\n"  % nexusprocessing.escape_nexus_token(title))
        if domain_taxon_namespace_title is None:
            domain_taxon_namespace_title = _compose_title(self.domain_taxon_namespace)
        if range_taxon_namespace_title is None:
            range_taxon_namespace_title = _compose_title(self.range_taxon_namespace)
        out.write("    TAXA %s, %s;\n" % (
            nexusprocessing.escape_nexus_token(range_taxon_namespace_title),
            nexusprocessing.escape_nexus_token(domain_taxon_namespace_title)
            ))
        out.write("    ASSOCIATES\n")
        out.write(self.mesquite_association_rows() + "\n")
        out.write("    ;\n")
        out.write("END;\n")
