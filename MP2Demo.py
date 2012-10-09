#!/usr/bin/python
# -*- coding: utf-8-*-

'''
==========
MP2Demo.py
==========
A demonstrator for CEDA_R miniprojects, iteration 2
Author: Albert Meroño-Peñuela
Version: 0.1
'''

from SPARQLWrapper import SPARQLWrapper, JSON, POST
from rdflib import URIRef
import os
import sys    
import datetime


class CEDARDemonstrator(object):
    # Define constants
    iteration = 2
    version = 0.1

    def __init__(self):
        # Set SPARQL endpoint
        self.sparql = SPARQLWrapper('http://localhost:8890/sparql')

        # Prefetch data on years
        self.sparql.setQuery("""
            SELECT DISTINCT ?g WHERE {GRAPH ?g {?s ?p ?o}}
        """)
        self.sparql.setReturnFormat(JSON)
        self.results = self.sparql.query().convert()
        self.yearsData = []
        self.yearsAnnotations = []
        for result in self.results["results"]["bindings"]:
            uriYear = {}
            uriYear["uri"] = URIRef(result["g"]["value"])
            uriYear["year"] = uriYear["uri"].split('/')[-1].split('_')[1]
            if uriYear["uri"].split('/')[3] == 'data':
                self.yearsData.append(uriYear)
            else:
                self.yearsAnnotations.append(uriYear)

        # Prefetch data on municipalities
        self.sparql.setQuery("""
            PREFIX d2s: <http://www.data2semantics.org/core/>
            PREFIX ns1: <http://www.data2semantics.org/core/NOORDBRABANT/>

            SELECT DISTINCT ?municipalityLabel WHERE {
                ?cell d2s:isObservation ?t .
                ?t ns1:GEMEENTEN ?municipality .
                ?municipality skos:prefLabel ?municipalityLabel .
            }
        """)
        self.sparql.setReturnFormat(JSON)
        self.results = self.sparql.query().convert()
        self.municipalities = []
        for result in self.results["results"]["bindings"]:
          self.municipalities.append(result["municipalityLabel"]["value"])

        # Preset center/outskirts
        self.outskirts = [
          'Center',
          'Outskirts',
          'Both'
          ]

        # Prefetch variables
        self.sparql.setQuery("""
            PREFIX d2s: <http://www.data2semantics.org/core/>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

            SELECT DISTINCT ?dimensionLabel WHERE {
                ?cell a d2s:ColHeader .
                ?cell d2s:isDimension ?dimension .
                ?dimension a d2s:Dimension ;
                           skos:prefLabel ?dimensionLabel .
            }
        """)
        self.sparql.setReturnFormat(JSON)
        self.results = self.sparql.query().convert()
        self.variables = []
        for result in self.results["results"]["bindings"]:
          self.variables.append(result["dimensionLabel"]["value"])

        # Preset annotations
        self.annotationsQuery = [
          'No',
          'Yes'
          ]
          

        # Query configuration parameters initialization

        self.startYear = 1
        self.endYear = 1
        self.province = 'Noord-Brabant'
        self.municipality = 141
        self.outskirt = 1
        self.var1 = 1
        self.var2 = 7
        self.var3 = 8
        self.annotation = 1


    def runQuery(self):
        '''
        Runs SPARQL query with current query configuration
        '''
        os.system('clear')
        print '-------------'
        print 'Query results'
        print '-------------'
        self.sparql.setQuery("""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX d2s: <http://www.data2semantics.org/core/>
            PREFIX qb: <http://purl.org/linked-data/cube#>
            PREFIX ns1: <http://www.data2semantics.org/core/NOORDBRABANT/>
            PREFIX ns2: <http://www.data2semantics.org/core/Noord-Brabant/> 

            SELECT ?value ?cell
            WHERE {
            { 
                ?municipality skos:prefLabel \"""" + self.municipalities[self.municipality-1]  + """\"@nl .
                ?cell d2s:isObservation ?b .
                ?b ns1:GEMEENTEN ?municipality .
                ?b a qb:Observation .
                ?b d2s:dimension ?dimension .
                ?dimension skos:prefLabel \"""" + self.variables[self.var1-1] + """\"@nl .
                OPTIONAL { ?dimension skos:prefLabel \"""" + self.variables[self.var2-1] + """\"@nl . }
                OPTIONAL { ?dimension skos:prefLabel \"""" + self.variables[self.var3-1] + """\"@nl . }
                ?b d2s:hasValue ?value .
            } UNION
            {
                ?municipality skos:prefLabel \"""" + self.municipalities[self.municipality-1]  + """\"@nl .
                ?cell d2s:isObservation ?b .
                ?b ns2:Gemeenten ?municipality .
                ?b a qb:Observation .       
                ?b d2s:dimension ?dimension .
                ?dimension skos:prefLabel \"""" + self.variables[self.var1-1] + """\"@nl .
                OPTIONAL { ?dimension skos:prefLabel \"""" + self.variables[self.var2-1] + """\"@nl . }
                OPTIONAL { ?dimension skos:prefLabel \"""" + self.variables[self.var3-1] + """\"@nl . }
                ?b d2s:hasValue ?value .
            }
            }
        """)

        self.sparql.setReturnFormat(JSON)
        self.resultset = self.sparql.query().convert()

        for result in self.resultset["results"]["bindings"]:
            print result["value"]["value"]

        print
        print 'Press the Enter key to return to main menu'
        ch = raw_input()

    def runAnnotationsQuery(self):
        '''
        Runs query for retrieving annotations of current resultset
        '''

        self.sparql.setQuery("""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX d2s: <http://www.data2semantics.org/core/>
            PREFIX qb: <http://purl.org/linked-data/cube#>
            PREFIX ns1: <http://www.data2semantics.org/core/NOORDBRABANT/>
            PREFIX ns2: <http://www.data2semantics.org/core/Noord-Brabant/> 
            PREFIX oa: <http://www.w3.org/ns/openannotation/core/>

            SELECT ?value ?cell ?flag ?cellLabel ?author ?annotated
            WHERE {
            { 
                ?municipality skos:prefLabel \"""" + self.municipalities[self.municipality-1]  + """\"@nl .
                ?cell d2s:isObservation ?b .
                ?cell d2s:cell ?cellLabel .
                ?b ns1:GEMEENTEN ?municipality .
                ?b a qb:Observation .
                ?b d2s:dimension ?dimension .
                ?dimension skos:prefLabel \"""" + self.variables[self.var1-1] + """\"@nl .
                OPTIONAL { ?dimension skos:prefLabel \"""" + self.variables[self.var2-1] + """\"@nl . }
                OPTIONAL { ?dimension skos:prefLabel \"""" + self.variables[self.var3-1] + """\"@nl . }
                ?b d2s:hasValue ?value .
                ?annotation oa:hasTarget ?cell .
                ?annotation oa:hasBody ?c .
                ?c rdf:value ?flag .
                ?annotation oa:annotated ?annotated .
                ?annotation oa:annotator ?author .
            } UNION
            {
                ?municipality skos:prefLabel \"""" + self.municipalities[self.municipality-1]  + """\"@nl .
                ?cell d2s:isObservation ?b .
                ?cell d2s:cell ?cellLabel .
                ?b ns2:Gemeenten ?municipality .
                ?b a qb:Observation .       
                ?b d2s:dimension ?dimension .
                ?dimension skos:prefLabel \"""" + self.variables[self.var1-1] + """\"@nl .
                OPTIONAL { ?dimension skos:prefLabel \"""" + self.variables[self.var2-1] + """\"@nl . }
                OPTIONAL { ?dimension skos:prefLabel \"""" + self.variables[self.var3-1] + """\"@nl . }
                ?b d2s:hasValue ?value .
                ?annotation oa:hasTarget ?cell .
                ?annotation oa:hasBody ?c .
                ?c rdf:value ?flag .
                ?annotation oa:annotated ?annotated .
                ?annotation oa:annotator ?author .
            }
            }
        """)

        self.sparql.setReturnFormat(JSON)
        self.annotationsResultset = self.sparql.query().convert()

        self.annotations = []
        for result in self.annotationsResultset["results"]["bindings"]:
            annotationStruct = {}
            annotationStruct["flag"] = result["flag"]["value"]
            annotationStruct["cell"] = result["cellLabel"]["value"]
            annotationStruct["annotated"] = result["annotated"]["value"]
            annotationStruct["author"] = result["author"]["value"]
            self.annotations.append(annotationStruct)

    def checkBenfordsLaw(self):
        '''
        Checks Benford's Law for the currently selected start year
        '''

        query = """
                PREFIX d2s: <http://www.data2semantics.org/core/>
          
                SELECT ?value WHERE {
                    ?cell d2s:hasValue ?value .
                }
                """
        # print query

        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        self.dataResultset = self.sparql.query().convert()

        self.benfordFreq = {}
        totalValues = 0
        for result in self.dataResultset["results"]["bindings"]:
            leadingDigit = str(result["value"]["value"])[0]
            try:
                self.benfordFreq[leadingDigit] += 1
            except KeyError:
                self.benfordFreq[leadingDigit] = 1
            totalValues += 1


        print 'Benford countings for current table'
        print
        print '-------------------'
        print ' D | f(D) |  rate  '
        print '-------------------'
        for i in range(1,10):
            print '{}    {}    {}'.format(i, self.benfordFreq[str(i)], float(self.benfordFreq[str(i)]/float(totalValues)))
        print
        print 'Press the Enter key to continue'
        ch = raw_input()
        


    def enterSetConfigMenu(self):
        '''
        Loop controller for setting query config menu
        '''

        self.printSetConfigMenu()
        ch = raw_input('--> ')
        while ch != '10':
            if ch == '1':
                self.enterStartYearMenu()
            elif ch == '2':
                self.enterEndYearMenu()
            elif ch == '3':
                print 'bar'
            elif ch == '4':
                self.enterMunicipalityMenu()
            elif ch == '5':
                self.enterCenterMenu()
            elif ch == '6':
                self.enterVar1Menu()
            elif ch == '7':
                self.enterVar2Menu()
            elif ch == '8':
                self.enterVar3Menu()
            elif ch == '9':
                self.enterSetAnnotationsMenu()

            else:
                print 'Invalid option'
            self.printSetConfigMenu()
            ch = raw_input('--> ')
        
        
        # Let the user select the time frame


    def enterStartYearMenu(self):
        '''
        Loop controller for the start year selection menu
        '''

        self.printStartYearMenu()

        ch = raw_input('--> ')
        self.startYear = int(ch)

    def enterEndYearMenu(self):
        '''
        Loop controller for the end year selection menu
        '''

        self.printEndYearMenu()
        ch = raw_input('--> ')
        self.endYear = int(ch)

    def enterMunicipalityMenu(self):
        '''
        Loop controller for the municipality selection menu
        '''

        self.printMunicipalityMenu()
        ch = raw_input('--> ')
        self.municipality = int(ch)

    def enterCenterMenu(self):
        '''
        Loop controller for the center/outskirts selection menu
        '''

        self.printCenterMenu()
        ch = raw_input('--> ')
        self.outskirt = int(ch)

    def enterVar1Menu(self):
        '''
        Loop controller for the first variable selection menu
        '''

        self.printVarMenu()
        ch = raw_input('--> ')
        self.var1 = int(ch)

    def enterVar2Menu(self):
        '''
        Loop controller for the second variable selection menu
        '''

        self.printVarMenu()
        ch = raw_input('--> ')
        self.var2 = int(ch)

    def enterVar3Menu(self):
        '''
        Loop controller for the third variable selection menu
        '''

        self.printVarMenu()
        ch = raw_input('--> ')
        self.var3 = int(ch)


    def enterSetAnnotationsMenu(self):
        '''
        Loop controller for the only annotated values menu
        '''

        self.printSetAnnotationsMenu()
        ch = raw_input('--> ')
        self.annotation = int(ch)

    def enterAnnotationsMenu(self):
        '''
        Loop controller for the annotations menu
        '''

        self.runAnnotationsQuery()

        self.printAnnotationsMenu()
        ch = raw_input('--> ')
        while ch != '4':
            if ch == '1':
                self.enterNewAnnotationMenu()
            elif ch == '2':
                self.enterEditAnnotationMenu()
            elif ch == '3':
                self.enterDeleteAnnotationMenu()
            else:
                print 'Invalid option'
            self.printAnnotationsMenu()
            ch = raw_input('--> ')

    def enterConsistencyMenu(self):
        '''
        Loop controller for the consistency menu
        '''

        self.printConsistencyMenu()
        ch = raw_input('--> ')
        while ch != '3':
            if ch == '1':
                self.checkTotals()
            elif ch == '2':
                self.checkBenfordsLaw()
            else:
                print 'Invalid option'
            self.printConsistencyMenu()
            ch = raw_input('--> ')


    def enterNewAnnotationMenu(self):
        '''
        Interactive input for a new annotation
        '''
        
        self.printNewAnnotationMenu()

        i = 1
        for year in self.yearsAnnotations:
          print '{}) {}'.format(i,year["year"])
          i += 1
        print
            
        year = raw_input('Table to annotate: ')
        cell = raw_input('Cell to annotate: ')
        author = raw_input('Author: ')
        corrected = raw_input('Corrected value (leave blank if none): ')
        flag = raw_input('Flag: ')

        graphURI = URIRef(self.yearsAnnotations[int(year)-1]["uri"])
        d2sGraphURI = graphURI.replace("cedar-project.nl", "www.data2semantics.org")
        annoURI = URIRef(d2sGraphURI + '/NOORDBRABANT/' + cell)
        cellURI = annoURI.replace("annotations", "data")

        # Create the new annotation
        query = """
            PREFIX oa: <http://www.w3.org/ns/openannotation/core/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            INSERT INTO GRAPH <""" + graphURI  + """>
            {
                <""" + annoURI  + """> a oa:Annotation;
                oa:annotated \"""" + str(datetime.datetime.now().strftime("%Y-%m-%d")) + """\"^^xsd:date;
                oa:annotator \"""" + author  + """\";
                oa:generated \"""" + str(datetime.datetime.now().strftime("%Y-%m-%d")) + """\"^^xsd:date;
                oa:generator <https://cedar-project.nl/tools/cedar-demo.py>;
                oa:hasBody [ rdf:value \"""" + corrected + ' ' + flag  + """\" ];
                oa:hasTarget <""" + cellURI  + """>;
                oa:modelVersion <http://www.openannotation.org/spec/core/20120509.html> .
            }
        """

        # query = "INSERT INTO GRAPH <http://cedar-project.nl/annotations/VT_1859_01_H1> {<http://a> rdf:type <http:b>}"

        print query

        self.sparql.setQuery(query)

        self.sparql.setReturnFormat(JSON)
        self.results = self.sparql.query().convert()
            
      
    def enterMainMenu(self):
        '''
        Main loop controller for the demonstrator menu
        '''
        
        self.printMainMenu()
        ch = raw_input('--> ')
        while ch != '5':
            if ch == '1':
                self.enterSetConfigMenu()
            elif ch == '2':
                self.runQuery()
            elif ch == '3':
                self.enterAnnotationsMenu()
            elif ch == '4':
                self.enterConsistencyMenu()
            else:
                print 'Invalid option'
            self.printMainMenu()
            ch = raw_input('--> ')

        os.system('clear')
        print 'Thanks for demoing CEDAR. Bye!'
        exit

    def printCurrentConfig(self):
        '''
        Prints current query configuration
        '''

        print 'Current query configuration:'
        print 
        print 'Start year: {}'.format(self.yearsData[int(self.startYear)-1]["year"])
        print 'End year: {}'.format(self.yearsData[int(self.endYear)-1]["year"])
        print 'Provice: {}'.format(self.province)
        print 'Municipality: {}'.format(self.municipalities[self.municipality-1])
        print 'Center/outskirts: {}'.format(self.outskirts[self.outskirt-1])
        print 'Selected variable 1: {}'.format(self.variables[self.var1-1])
        print 'Selected variable 2: {}'.format(self.variables[self.var2-1])
        print 'Selected variable 3: {}'.format(self.variables[self.var3-1])
        print 'Only annotated values: {}'.format(self.annotationsQuery[self.annotation-1])

    def printCurrentAnnotations(self):
        '''
        Prints the annotations for the resultset of current query configuration
        '''

        print 'Annotations on current query resultset:'
        print
        for annotation in self.annotations:
            print 'Annotation at {}, author {}, annotated at {}'.format(annotation["cell"], annotation["author"], annotation["annotated"])
            print 'Flag: "{}"'.format(annotation["flag"])
            print

    def printNewAnnotationMenu(self):
        '''
        Prints the interactive questions for a new annotation
        '''

        os.system('clear')
        print '--------------'
        print 'New annotation'
        print '--------------'
        print 'Please answer the questions an press the Enter key.'
        print
        

    def printStartYearMenu(self):
        '''
        Prints start year menu once
        '''

        os.system('clear')
        print '---------------'
        print 'Available years'
        print '---------------'
        i = 1
        for year in self.yearsData:
            print '{}) {}'.format(i,year["year"])
            i += 1
        print
        print 'Type your choice:'

    def printEndYearMenu(self):
        '''
        Prints end year menu once
        '''

        os.system('clear')
        print '---------------'
        print 'Available years'
        print '---------------'
        i = 1
        for year in self.yearsData:
            print '{}) {}'.format(i,year["year"])
            i += 1
        print
        print 'Type your choice:'

    def printMunicipalityMenu(self):
        '''
        Prints the municipality selection menu once
        '''

        os.system('clear')
        print '------------------------'
        print 'Available municipalities'
        print '------------------------'
        i = 1
        for municipality in self.municipalities:
          print '{}) {}'.format(i,municipality)
          i += 1
        print
        print 'Type your choice:'

    def printCenterMenu(self):
        '''
        Prints the center/outskirts selection menu once
        '''

        os.system('clear')
        print '-------------------------------------'
        print 'Available options on center/outskirts'
        print '-------------------------------------'
        i = 1
        for outskirt in self.outskirts:
          print '{}) {}'.format(i,outskirt)
          i += 1
        print
        print 'Type your choice and then press the Enter key:'

    def printSetAnnotationsMenu(self):
        '''
        Prints the annotated values selection menu once
        '''

        os.system('clear')
        print '-------------------------------------'
        print 'Available options on annotated values'
        print '-------------------------------------'
        i = 1
        for annotation in self.annotationsQuery:
          print '{}) {}'.format(i,annotation)
          i += 1
        print
        print 'Type your choice and then press the Enter key:'

    def printVarMenu(self):
        '''
        Prints the variable selection menu once
        '''

        os.system('clear')
        print '----------------------------'
        print 'Available variables to query'
        print '----------------------------'
        i = 1
        for variable in self.variables:
          print '{}) {}'.format(i,variable)
          i += 1
        print
        print 'Type your choice and then press the Enter key:'

    def printSetConfigMenu(self):
        '''
        Prints menu for setting query config
        '''
        
        os.system('clear')
        print '------------------------'
        print 'Query configuration menu'
        print '------------------------'
        print '1) Set start year'
        print '2) Set end year'
        print '3) Set province'
        print '4) Set municipality'
        print '5) Set center/outskirts'
        print '6) Set variable 1'
        print '7) Set variable 2'
        print '8) Set variable 3'
        print '9) Set annotated values'
        print '10) Go back'
        print
        print 'Type your choice and then press the Enter key:'

    def printAnnotationsMenu(self):
        '''
        Prints annotations menu
        '''
        
        os.system('clear')
        print '------------------------'
        print 'Annotations menu'
        print '------------------------'
        self.printCurrentAnnotations()
        print
        print '1) Create a new annotation'
        print '2) Edit an existing annotation'
        print '3) Delete an existing annotation'
        print '4) Go back'
        print
        print 'Type your choice and then press the Enter key:'

    def printConsistencyMenu(self):
        '''
        Prints consistency menu
        '''
        
        os.system('clear')
        print '-------------------------'
        print 'Consistency checking menu'
        print '-------------------------'
        print
        print '1) Check totals of current query configuration'
        print '2) Check Benford\'s Law in currently selected start year'
        print '3) Go back'
        print
        print 'Type your choice and then press the Enter key:'



    def printMainMenu(self):
        '''
        Prints demonstrator menu once
        '''

        os.system('clear')
        print '================================================='
        print 'CEDAR miniproject demonstrator, iteration {}, v{}'.format(self.iteration,self.version)
        print '================================================='
        self.printCurrentConfig()
        print
        print '---------'
        print 'Main menu'
        print '---------'
        print '1) Change query configuration'
        print '2) Run query with current configuration and show results'
        print '3) Annotations menu'
        print '4) Consistency checking menu'
        print '5) Exit'
        print
        print 'Type your choice and then press the Enter key:'


if __name__ == '__main__':

    print 'CEDAR demonstrator loading, please wait...'
    d = CEDARDemonstrator()
    d.enterMainMenu()
