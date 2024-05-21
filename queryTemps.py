##getEntity
#get entity URI (people, movie)
EntURIQueryTemp = '''
    prefix wdt: <http://www.wikidata.org/prop/direct/>
    prefix wd: <http://www.wikidata.org/entity/>
    
    SELECT ?uri
    WHERE{{
        ?uri rdfs:label "{}"@en.
        {{?uri wdt:P31 wd:Q11424 .}}
        UNION
        {{?uri wdt:P31 wd:Q5.}}
        UNION
        {{?uri wdt:P31 wd:Q20650540.}}
        UNION
        {{?uri wdt:P31 wd:Q29168811.}}
        }}'''

##getRelation
#get relation URI
RelURIQueryTemp = '''
    prefix wdt: <http://www.wikidata.org/prop/direct/>
    prefix wd: <http://www.wikidata.org/entity/>
    
    SELECT ?uri WHERE{{
        ?uri rdfs:label "{}"@en.
        }}'''

##getAnswer
#direct get answer with entity id and relation id
directQueryTemp = '''
    prefix wdt: <http://www.wikidata.org/prop/direct/>
    prefix wd: <http://www.wikidata.org/entity/>

    SELECT ?objU
    WHERE {{
        wd:{} wdt:{} ?objU.
    }}'''

#embedding query
embeddingQueryTemp = '''
    prefix wdt: <http://www.wikidata.org/prop/direct/>
    prefix wd: <http://www.wikidata.org/entity/>

    SELECT ?objU
    WHERE {{
        ?sujU rdfs:label "{}"@en.
        {{?sujU wdt:P31 wd:Q11424 .}}
        UNION
        {{?sujU wdt:P31 wd:Q5.}}
        ?sujU wdt:{} ?objU.
}}'''

#entity id
entIdQueryTemp = '''
    prefix wdt: <http://www.wikidata.org/prop/direct/>
    prefix wd: <http://www.wikidata.org/entity/>

    SELECT ?label
    WHERE {{
    wd:{} rdfs:label ?label.
        }}'''



##getImages
#get entity(person)
personQueryTemp = '''
    prefix wdt: <http://www.wikidata.org/prop/direct/>
    prefix wd: <http://www.wikidata.org/entity/>
    
    SELECT ?person WHERE {{
        ?person rdfs:label "{}"@en .
        ?person wdt:P31 wd:Q5.
    }}'''

#get entity(movie)
movieQueryTemp = '''
    prefix wdt: <http://www.wikidata.org/prop/direct/>
    prefix wd: <http://www.wikidata.org/entity/>
    
    SELECT ?movie WHERE {{
        ?movie rdfs:label "{}"@en .
        ?movie wdt:P31 wd:Q11424.
    }}'''

#imdb id of movie
movieIdQueryTemp = '''
    prefix wdt: <http://www.wikidata.org/prop/direct/>
    prefix wd: <http://www.wikidata.org/entity/>
    
    SELECT ?imdb WHERE {{
        ?qid rdfs:label "{}"@en .
        ?qid wdt:P345 ?imdb .
        FILTER(STRSTARTS(str(?imdb), "tt")) .
    }}'''

#imbd id of people
humanIdQueryTemp = '''
    prefix wdt: <http://www.wikidata.org/prop/direct/>
    prefix wd: <http://www.wikidata.org/entity/>
    
    SELECT ?imdb
    WHERE {{
        ?qid rdfs:label "{}"@en .
        ?qid wdt:P345 ?imdb .
        FILTER(STRSTARTS(str(?imdb), "nm")) .
        }}'''

##getRecommendation
#get genre of movie
movieGenreQueryTemp = '''
    prefix wdt: <http://www.wikidata.org/prop/direct/>
    prefix wd: <http://www.wikidata.org/entity/>
    
    SELECT ?genre
    WHERE {{
        ?movie rdfs:label "{}"@en .
        ?movie wdt:P136 ?genre .
        }}'''



