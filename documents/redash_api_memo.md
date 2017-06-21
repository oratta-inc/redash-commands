## 参考リンク
[Redash API](https://people-mozilla.org/~ashort/redash_docs/api.html)

## API疎通時に得られるオブジェクトの例
#### Queryオブジェクト
```json
{
    "query_hash":"c9b37dae574326739fe6abde0d3d477b",
    "visualizations":[
        {
            "name":"Table",
            "id":98,
            "type":"TABLE",
            "created_at":"2017-05-30T14:34:11.489512+09:00",
            "updated_at":"2017-05-30T14:34:11.489512+09:00",
            "description":"",
            "options":{}
        }
    ],
    "query":"SELECT 1 {{parameter}};",
    "last_modified_by":{
        "name":"(対象ユーザ名)",
        "grava_url":"(対象アカウントのgravatar URL)",
        "auth_type":"password",
        "created_at":"2017-04-06T10:31:20.844739+09:00",
        "id":2,
        "updated_at":"2017-05-02T16:13:24.172251+09:00",
        "email":"(対象アカウントのメールアドレス)",
        "groups":[
             2,
             3,
             1
        ]
    },
    "can_edit":True,
    "created_at":"2017-05-30T14:34:11.489512+09:00",
    "user":{
        "name":"(対象ユーザ名)",
        "grava_url":"(対象アカウントのgravatar URL)",
        "auth_type":"password",
        "created_at":"2017-04-06T10:31:20.844739+09:00",
        "id":2,
        "updated_at":"2017-05-02T16:13:24.172251+09:00",
        "email":"(対象アカウントのメールアドレス)",
        "groups":[
             2,
             3,
             1
        ]
    },
    "description":None,
    "is_archived":False,
    "name":"ARPPU #API疎通用サンプル",
    "id":48,
    "version":1,
    "updated_at":"2017-06-15T14:25:33.216603+09:00",
    "schedule":None,
    "data_source_id":2,
    "api_XL3o9ONQKr4MrU524PV86On3II1Bo7jRyj3kXJqG",
    "is_draft":True,
    "options":{
        "parameters":[
            {
                "name":"parameter",
                "value":"2017-06-15 04:24",
                "global":False,
                "type":"datetime-local",
                "title":"parameter"
            }
        ]
    },
    "latest_query_data_id":936
}
```

#### Jobオブジェクト
```json
{
    "job":{
        "query_result_id": None,
        "id": "b2009309-33ef-4380-8c75-7f3419330e0a",
        "error": "",
        "updated_at": 0,
        "status": 2
    }
}
```
