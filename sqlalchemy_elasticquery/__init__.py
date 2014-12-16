"""
    SQLAlchemy-ElasticQuery
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    Modulo que permite usar la sintaxis de busqueda de ES en SQLAlchemy.
    Crea un objeto SQLAlchemy query y devuelve la query lista

    {
        "filter" : {
            "or" : {
                "firstname" : {
                    "equals" : "joel"
                },
                "lastname" : "joel",
                "uid" : {
                    "like" : "joel"
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
    :license: GNU AGPLv3+ or BSD
"""
import json
from sqlalchemy import and_, or_

__version__ = '0.0.1'

def elastic_query(model, query, session):
    instance = ElasticQuery(model, query, session)
    instance.search()
    return True

OPERATORS = {
        'like': lambda f, a: f.like(a),
        'equals': lambda f, a: f == a,
        'is_null': lambda f: f == None,
        'is_not_null': lambda f: f != None,
        'gt': lambda f, a: f > a,
        'gte': lambda f, a: f >= a,
        'lt': lambda f, a: f < a,
        'lte': lambda f, a: f <= a,
        'in': lambda f, a: f.in_(a),
        'not_in': lambda f, a: ~f.in_(a),
        'not_equal_to': lambda f, a: f != a
    }

class ElasticQuery(object):

    def __init__(self, model, query, session):
        """ Inicializar de la clase 'ElasticQuery'
        """
        self.model = model
        self.query = query
        self.session = session # es opcional hacer la compatibilidad con flask
        self.model_query = self.session.query(self.model) #variable model query es soooo important


    def search(self):
        """ Es el metodo mas importante, inicializa el proceso y deriva en demas metodos
        """
        # TODO: exepcion si esta mal formado o dmas
        filters = json.loads(self.query)
        
        if filters['filter'] is not None:
            print self.parse_filter(filters['filter'])
        # if filters['sort'] is not None:
            # do sort
            # pass


    def parse_filter(self, filters):
        """ Este metodo se encarga de procesar los filtros y devuelve <model.query>
        """
        model_query = self.model_query
        for filter_type in filters:
            if filter_type == 'or' or filter_type == 'and':
                conditions = []
                for field in filters[filter_type]:
                    # check is field es operator or field and append to conditions
                    conditions.append(self.create_query(self.parse_field(field, filters[filter_type][field])))
                if filter_type == 'or':
                    model_query = self.model_query.filter(or_(*conditions))
                elif filter_type == 'and':
                    model_query = self.model_query.filter(and_(*conditions))
            else:
                #TODO: esta parte
                pass
                
        return model_query
                    
    def parse_field(self, field, field_value):
        if type(field_value) is dict:
            # TODO: verificar si el operador existe sino error
            operator = field_value.keys()[0]
            if self.verify_operator(operator) is False:
                return "Error: operador no exite", operator
            value = field_value[operator]
        elif type(field_value) is unicode:
            operator = u'equals'
            value =  field_value
        return field, operator, value

    def verify_operator(self, operator):
        # print 'operator', operator
        try:
            if hasattr(OPERATORS[operator], '__call__'):
                return True
            else:
                return False
        except:
            return False

    def create_query(self, attr):
        field = attr[0]
        operator = attr[1]
        value = attr[2]
        model = self.model
        return OPERATORS[operator](getattr(model, field, None), value)