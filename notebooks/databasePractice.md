# Movie Database ERD

```mermaid
erDiagram
    MOVIE {
        int movie_id PK
        int year
        int eps
        decimal scores
    }

    ACTOR {
        int actor_id PK
        string actor_name
    }

    WRITER {
        int writer_id PK
        string writer_name
    }

    SHOW_TYPE {
        int type_id PK
        string type_name
    }

    GENRE {
        int genre_id PK
        string genre_name
    }

    MOVIE }o--o{ ACTOR : features
    MOVIE }o--o{ WRITER : written_by
    MOVIE }o--o{ GENRE : categorized_as
    SHOW_TYPE ||--o{ MOVIE : classifies
```

        