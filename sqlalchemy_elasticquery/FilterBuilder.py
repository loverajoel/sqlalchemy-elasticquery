# The MIT License (MIT)
#
# Copyright (c) 2016 Doss Gunter
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# FilterBuilder works with elastic-query and sqlalchemy to make it easier to
# make dynamic querys.  Hope someone finds it useful!

# USAGE:
#
# make a FilterBuilder passing sqlalchemy ORM class
# myfilter = FilterBuilder(myClass)
# add a And or Or filters arguments are:
#                    column, operator, value
# myfilter.addAndFilter("id", "lt", "45")
# queryString = myfilter.buildQuery()


from sqlalchemy import inspect as sqlalchemy_inspect
from collections import defaultdict


class FilterBuilder(object):
    """A filter builder for the elastic-query extention for sqlalchemy
    https://github.com/loverajoel/sqlalchemy-elasticquery"""
    """Takes a sqlalchemy ORM class"""

    def __init__(self, ObjectClass):
        self._orFilters = defaultdict(self.default_factory)
        self._andFilters = defaultdict(self.default_factory)
        self._valid = True
        self.needsBuilt = False
        module = sqlalchemy_inspect(ObjectClass)
        self._columnList = module.column_attrs.keys()
        self._operators = {
            'like', 'equals', 'is_null',
            'is_not_null', 'gt', 'gte',
            'lt', 'lte', 'in',
            'not_in', 'not_equal_to'
        }

    def default_factory(self):
        return defaultdict(dict)

        """Checks for a valid filter."""

    def Valid(self):
        if len(self._orFilters) > 0 or len(self._andFilters) > 0:
            return True
        return False

    def clearFilter(self, filterTarget, filterType=None):
        """Delete a filter from the dicts.  If filterType is given will only delete the given type"""
        if filterTarget in self._orFilters:
            self.needsBuilt = True
            if filterType:
                del self._orFilters[filterTarget][filterType]
            else:
                del self._orFilters[filterTarget]

        if filterTarget in self._andFilters:
            self.needsBuilt = True
            if filterType:
                del self._andFilters[filterTarget][filterType]
            else:
                del self._andFilters[filterTarget]

    def addOrFilter(self, filterTarget, filterType, filterValue):
        """filterTarget = column to filter, filterType = operator, filterValue = operation
        ex. addOrFilter("id", "lt", "30")"""
        if filterType not in self._operators:
            print("Error: Filter Type not known")
            self._valid = False
            return False
        if filterTarget not in self._columnList:
            print("Error: Filter Target not valid")
            self._valid = False
            return False
        targetDict = self._orFilters[filterTarget]
        targetDict[filterType] = filterValue
        self.needsBuilt = True
        return True

    def addAndFilter(self, filterTarget, filterType, filterValue):
        """filterTarget = column to filter, filterType = operator, filterValue = operation
        ex. addAndFilter("id", "lt", "30")"""
        if filterType not in self._operators:
            print("Error: Filter Type not known")
            self._valid = False
            return False
        if filterTarget not in self._columnList:
            print("Error: Filter Target not valid")
            self._valid = False
            return False
        targetDict = self._andFilters[filterTarget]
        targetDict[filterType] = filterValue
        self.needsBuilt = True
        return True

    def _buildSubQuery(self, whichDict, and_or, queryString):
        if len(whichDict) > 0:
            first_run = True
            for target in whichDict.keys():
                typeDict = whichDict[target]
                for eachType in typeDict.keys():
                    if first_run:
                        queryString += '"%s" :{ ' % and_or
                        queryString += '"%s" : {"%s" : "%s"}' % (
                            target, eachType, typeDict[eachType])
                        first_run = False
                    else:
                        queryString += ',"%s" : {"%s" : "%s"}' % (
                            target, eachType, typeDict[eachType])
        queryString += '}'
        return queryString

    def buildQuery(self):
        """returns the queryString."""
        if not self.Valid:
            print("Invalid usage: cannot build.")
            return False
        if not self.needsBuilt:
            return self.queryString

        queryString = '{"filter" : {'
        orAdded = False

        if len(self._orFilters) > 0:
            queryString = self._buildSubQuery(
                self._orFilters, "or", queryString)
            orAdded = True

        if orAdded and len(self._andFilters) > 0:
            queryString += ','

        if len(self._andFilters) > 0:
            queryString = self._buildSubQuery(
                self._andFilters, "and", queryString)

        queryString += '}}'
        self.queryString = queryString
        return queryString
