# TV Show Database ERD

```mermaid
erDiagram
    TV_SHOW {
        int tv_show_id PK
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

    TV_SHOW }o--o{ ACTOR : features
    TV_SHOW }o--o{ WRITER : written_by
    TV_SHOW }o--o{ GENRE : categorized_as
    SHOW_TYPE ||--o{ TV_SHOW : classifies
```



        
