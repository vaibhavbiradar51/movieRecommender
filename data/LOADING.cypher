drop constraint actor_id_pk;
drop index actor_name;
MATCH (a:Actor) DETACH DELETE a; CREATE INDEX actor_name IF NOT EXISTS FOR (a:Actor) ON (a.Name); CREATE CONSTRAINT actor_id_pk IF NOT EXISTS ON (a:Actor) ASSERT a.actor_ID IS UNIQUE; LOAD CSV WITH HEADERS FROM "file:///movie_actors.csv" AS actor_row MERGE (a:Actor {actor_ID:actor_row.actorID,name:actor_row.actorName});

drop index director_name;
drop index director_id;
MATCH (d:Director) DETACH DELETE d; CREATE INDEX director_name IF NOT EXISTS FOR (d:Director) ON (d.name); CREATE INDEX director_id IF NOT EXISTS FOR (d:Director) ON (d.director_ID); LOAD CSV WITH HEADERS FROM "file:///movie_directors.csv" AS director_row MERGE (d:Director {director_ID:director_row.directorID,name:director_row.directorName});

drop constraint genre_pk;
MATCH (g:Genre) DETACH DELETE g; CREATE CONSTRAINT genre_pk IF NOT EXISTS ON (g:Genre) ASSERT g.genre IS UNIQUE; LOAD CSV WITH HEADERS FROM "file:///movie_genres.csv" AS genre_row MERGE (g:Genre {genre:genre_row.genre});

drop constraint country_pk;
MATCH (c:Country) DETACH DELETE c; 
CREATE CONSTRAINT country_pk IF NOT EXISTS ON (c:Country) ASSERT c.country IS UNIQUE; LOAD CSV WITH HEADERS FROM "file:///movie_countries.csv" AS country_row MERGE (c:Country {country:country_row.country});

drop constraint movie_id_pk;
drop index movie_title;
MATCH (m:Movie) DETACH DELETE m; CREATE INDEX movie_title IF NOT EXISTS FOR (m:Movie) ON (m.title); CREATE CONSTRAINT movie_id_pk IF NOT EXISTS ON (m:Movie) ASSERT m.movie_ID IS UNIQUE; LOAD CSV WITH HEADERS FROM "file:///movies.csv" AS movie_row MERGE (m:Movie {movie_ID:movie_row.id, title:movie_row.title, criticsRating:movie_row.criticsRating, year:movie_row.year, imageURL:movie_row.pictureURL});

drop index user_name;
CREATE INDEX user_name IF NOT EXISTS FOR (u:User) ON (u.name); CREATE CONSTRAINT user_id_pk IF NOT EXISTS ON (u:User) ASSERT u.ID IS UNIQUE;

CREATE CONSTRAINT friendship_id_pk IF NOT EXISTS ON (f:Friendship) ASSERT (f.ID1, f.ID2) IS NODE KEY;