LOAD CSV WITH HEADERS FROM "file:///movie_actors.csv" AS actor_row MATCH (m:Movie{movie_ID:actor_row.movieID}) MATCH (a:Actor{actor_ID:actor_row.actorID}) MERGE (m)-[:movieActor{ranking:actor_row.ranking}]->(a);

LOAD CSV WITH HEADERS FROM "file:///movie_countries.csv" AS country_row MATCH (m:Movie{movie_ID:country_row.movieID}) MATCH (c:Country{country:country_row.country}) MERGE (m)-[:movieCountry]->(c);

LOAD CSV WITH HEADERS FROM "file:///movie_directors.csv" AS director_row MATCH (m:Movie{movie_ID:director_row.movieID}) MATCH (d:Director{director_ID:director_row.directorID}) MERGE (m)-[:movieDirector]->(d);

LOAD CSV WITH HEADERS FROM "file:///movie_genres.csv" AS genre_row MATCH (m:Movie{movie_ID:genre_row.movieID}) MATCH (g:Genre{genre:genre_row.genre}) MERGE (m)-[:movieGenre]->(g);

MATCH (m:Movie)
SET m.criticsRating = toFloat(m.criticsRating);

MATCH (m:Movie)
SET m.year = toInteger(m.year);

MATCH (m:Movie)
SET m.isURL = 1;