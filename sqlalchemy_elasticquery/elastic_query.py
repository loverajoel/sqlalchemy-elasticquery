"""
    SQLAlchemy-ElasticQuery
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    This extension allow you use the ElasticSearch syntax for search in SQLAlchemy.
    Get a query string and return a SQLAlchemy query

    Example query string:

        {
            "filter" : {
                "or" : {
                    "firstname" : {
                        "equals" : "Jhon"
                    },
                    "lastname" : "Galt",
                    "uid" : {
                        "like" : "111111"
                    }
                },
                "and" : {
                    "status" : "active",
                    "age" : {
                        "gt" : 18
                    }
                }
            },
            "sort" : {
                { "firstname" : "asc" },
                { "age" : "desc" }
            }
        }

    :copyright: 2015 Joel Lovera <joelalovera@gmail.com>
"""
import json
from sqlalchemy import and_, or_, desc, asc

__version__ = '0.0.1'


def elastic_query(model, query, session = None):
    """ Public method for init the class ElasticQuery
        :model: SQLAlchemy model
        :query: valid string like a ElasticSearch
        :session: SQLAlchemy session *optional
    """
    # TODO: make session to optional
    instance = ElasticQuery(model, query, session)
    return instance.search()

""" Valid operators """
OPERATORS = {
    'like': lambda f, a: f.like(a),
    'equals': lambda f, a: f == a,
    'is_null': lambda f: f is None,
    'is_not_null': lambda f: f is not None,
    'gt': lambda f, a: f > a,
    'gte': lambda f, a: f >= a,
    'lt': lambda f, a: f < a,
    'lte': lambda f, a: f <= a,
    'in': lambda f, a: f.in_(a),
    'not_in': lambda f, a: ~f.in_(a),
    'not_equal_to': lambda f, a: f != a
    }


class ElasticQuery(object):
    """ Magic method """

    def __init__(self, model, query, session=None):
        """ Initializator of the class 'ElasticQuery' """
        self.model = model
        self.query = query
        if hasattr(model, 'query'):
            self.model_query = model.query
        else:
            self.model_query = session.query(self.model)

    def search(self):
        """ This is the most important method """
        # TODO: verify format and emit expetion
        filters = json.loads(self.query)
        result = self.model_query
        if 'filter'in filters.keys():
            result = self.parse_filter(filters['filter'])
        if 'sort'in filters.keys():
            result = result.order_by(*self.sort(filters['sort']))

        return result

    def parse_filter(self, filters):
        """ This method process the filters """
        for filter_type in filters:
            if filter_type == 'or' or filter_type == 'and':
                conditions = []
                for field in filters[filter_type]:
                    conditions.append(self.create_query(self.parse_field(field, filters[filter_type][field])))
                if filter_type == 'or':
                    self.model_query = self.model_query.filter(or_(*conditions))
                elif filter_type == 'and':
                    self.model_query = self.model_query.filter(and_(*conditions))
            else:
                conditions = self.create_query(self.parse_field(filter_type, filters[filter_type]))
                self.model_query = self.model_query.filter(conditions)
        return self.model_query

    def parse_field(self, field, field_value):
        """ Parse the operators and traduce: ES to SQLAlchemy operators """
        if type(field_value) is dict:
            # TODO: check operators and emit error
            operator = field_value.keys()[0]
            if self.verify_operator(operator) is False:
                return "Error: operador no exite", operator
            value = field_value[operator]
        elif type(field_value) is unicode:
            operator = u'equals'
            value = field_value
        return field, operator, value

    def verify_operator(self, operator):
        """ Verify if the operator is valid """
        try:
            if hasattr(OPERATORS[operator], '__call__'):
                return True
            else:
                return False
        except:
            return False

    def create_query(self, attr):
        """ Mix all values and make the query """
        field = attr[0]
        operator = attr[1]
        value = attr[2]
        model = self.model
        return OPERATORS[operator](getattr(model, field, None), value)

    def sort(self, sort_list):
        """ Sort """
        order = []
        for sort in sort_list:
            if sort_list[sort] == "asc":
                order.append(asc(getattr(self.model, sort, None)))
            elif sort_list[sort] == "desc":
                order.append(desc(getattr(self.model, sort, None)))
        return order
