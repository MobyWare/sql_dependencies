##*******************************************************
# Got these functions from https://github.com/andialbrecht/sqlparse/blob/master/examples/extract_table_names.py
##*********************************************************

#%%
import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML


def is_subselect(parsed):
    if not parsed.is_group:
        return False
    for item in parsed.tokens:
        if item.ttype is DML and item.value.upper() == 'SELECT':
            return True
    return False


def extract_from_part(parsed):
    from_seen = False
    for item in parsed.tokens:
        if from_seen:
            if is_subselect(item):
                yield from extract_from_part(item)
            elif item.ttype is Keyword:
                return
            else:
                yield item
        elif item.ttype is Keyword and item.value.upper() == 'FROM':
            from_seen = True


def extract_table_identifiers(token_stream):
    for item in token_stream:
        if isinstance(item, IdentifierList):
            for identifier in item.get_identifiers():
                yield identifier.get_name()
        elif isinstance(item, Identifier):
            yield item.get_name()
        # It's a bug to check for Keyword here, but in the example
        # above some tables names are identified as keywords...
        elif item.ttype is Keyword:
            yield item.value


def extract_tables(sql):
    stream = extract_from_part(sqlparse.parse(sql)[0])
    return list(extract_table_identifiers(stream))


#%%
##basic query
sql = """
select K.a,K.b from (select H.b from (select G.c from (select F.d from
(select E.e from A, B, C, D, E), F), G), H), I, J, K order by 1,2;
"""

#%%
##complex query; joins and ctes
## TODO - parsing CTE doesn't work. Also need a way to get table name not alias.
sql = """
with freq as (
select
    department_id
from
    employees e inner join departments d on d.department_id = e.department_id
group by 1
having
    count(distinct e.employee_id) > 5000
)
select 
    *
from
    employees e inner join freq f on f.department_id = d.department_id

"""

tables = ', '.join(extract_tables(sql))
print('Tables: {}'.format(tables))
# %%
