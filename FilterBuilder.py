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

# I just coded this real quick because I needed to dynamicly build queries and it
# was to much work with strings. I haven't tested it beyond a few simple queries
# but it works so far.

# USAGE:
#
# make a FilterBuilder
# myfilter = FilterBuilder(myClass)
# myfilter.addAndFilter("id", "lt", "45")
# queryString = myfilter.buildQuery()


from sqlalchemy import inspect as sqlalchemy_inspect


class FilterBuilder(object):
    """A filter builder for the elastic-query extention for sqlalchemy
    https://github.com/loverajoel/sqlalchemy-elasticquery"""
    """Takes a sqlalchemy ORM class"""

    def __init__(self, ObjectClass):
        self._orFilters = list()
        self._andFilters = list()
        self._valid = True
        module = sqlalchemy_inspect(ObjectClass)
        self._columnList = module.column_attrs.keys()
        ObjectClass
        self._operators = {
            'like', 'equals', 'is_null',
            'is_not_null', 'gt', 'gte',
            'lt', 'lte', 'in',
            'not_in', 'not_equal_to'
        }

    """Checks for a valid filter."""

    def Valid(self):
        if self._valid:
            if len(self._orFilters) > 0 and len(self._andFilters) > 0:
                return True
        return False

    """filterTarget = column to filter, filterType = operator, filterValue = operation
    ex. addOrFilter("id", "lt", "30")"""

    def addOrFilter(self, filterTarget, filterType, filterValue):
        if filterType not in self._operators:
            print "Error: Filter Type not known"
            self._valid = False
            return False
        if filterTarget not in self._columnList:
            print "Error: Filter Target not valid"
            self._valid = False
            return False
        self._orFilters.append((filterTarget, filterType, filterValue))
        return True

    """filterTarget = column to filter, filterType = operator, filterValue = operation
    ex. addAndFilter("id", "lt", "30")"""

    def addAndFilter(self, filterTarget, filterType, filterValue):
        if filterType not in self._operators:
            print "Error: Filter Type not known"
            self._valid = False
            return False
        if filterTarget not in self._columnList:
            print "Error: Filter Target not valid"
            self._valid = False
            return False
        self._andFilters.append((filterTarget, filterType, filterValue))
        return True

    def _buildSubQuery(self, whichList, and_or, queryString):
        # print "build %s: %s" % (and_or, queryString)
        if len(whichList) > 0:
            queryString += '"%s" :{ ' % and_or
            thisOr = whichList.pop()
            queryString += '"%s" : {"%s" : "%s"}' % (
                thisOr[0], thisOr[1], thisOr[2])
        if len(whichList) > 0:
            for each in whichList:
                queryString += ',"%s" : {"%s" : "%s"}' % (
                    each[0], each[1], each[2])
        queryString += '}'
        # print "end build %s: %s" % (and_or, queryString)
        return queryString

    """returns the queryString."""

    def buildQuery(self):
        if not self.Valid:
            print "Invalid usage: cannot build."
            return False
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
        self._valid = False
        return queryString
