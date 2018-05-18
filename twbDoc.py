import xml.etree.ElementTree
import attr
from pprint import pprint

@attr.s
class Workbook (object):
    filename = attr.ib()
    version = attr.ib()
    datasources = attr.ib (factory=dict)

@attr.s
class Calculation (object):
    pass

@attr.s
class TableauFormula (Calculation):
    formula = attr.ib()
    pass

@attr.s
class CategoricalBin (Calculation):
    basecolumn = attr.ib()

@attr.s
class RegularBin (Calculation):
    formula = attr.ib()

@attr.s
class Column (object):
    name = attr.ib()
    caption = attr.ib()
    datatype = attr.ib()
    calculation = attr.ib(default=None)
    hidden = attr.ib(default=False)

class Dimension (Column):
    pass

class Measure (Column):
    pass

class Parameter (Column):
    pass


@attr.s
class Datasource (object):
    name = attr.ib()
    columns = attr.ib(factory=list)


def parseWorkbook (filename):
    root = xml.etree.ElementTree.parse(filename).getroot()
    wb = Workbook (filename=filename, version=root.attrib.get('version', None))
    for datasource in root.find('datasources').findall('datasource'):
        ds = Datasource (name=datasource.attrib.get('name', None))
        wb.datasources[ds.name] = ds
        for column in datasource.findall('column'):
            if ds.name == 'Parameters':
                colclass = Parameter
            elif column.attrib['role'] == 'measure':
                colclass = Measure
            elif column.attrib['role'] == 'dimension':
                colclass = Dimension
            else:
                raise ValueError ("don't know what class to use for this column (%s)" % (repr(column)))
            a = column.attrib
            col = colclass(name=a['name'], caption=a.get('caption', a['name']), datatype=a['datatype'])
            calculation = column.find('calculation')
            if calculation is not None:
                classname = calculation.attrib.get('class', None)
                if classname=='tableau':
                    col.calculation = TableauFormula(formula=calculation.attrib['formula'])
                elif classname=='categorical-bin':
                    col.calculation = CategoricalBin(basecolumn=calculation.attrib['column'])
                elif classname=='bin':
                    col.calculation = RegularBin(formula=calculation.attrib['formula'])
                else:
                    raise ValueError ('Unknown calculation class "%s"' % (classname))
            ds.columns.append(col)

        #break

    return wb

pprint (parseWorkbook('testBook1.twb'))