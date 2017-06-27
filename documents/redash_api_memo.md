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

#### QueryResultオブジェクト
```json
{
    "query_result":{
        "retrieved_at":"2017-06-21T17:15:10.827623+09:00",
        "data_source_id":1,
        "id":1072,
        "data":{
            "columns":[
                 {
                    "friendly_name":"user_agent",
                    "name":"user_agent",
                    "type":"integer"
                 },
                 {
                    "friendly_name":"date",
                    "name":"date",
                    "type":"string"
                 },
                 {
                    "friendly_name":"purchase_amount_sum",
                    "name":"purchase_amount_sum",
                    "type":"integer"
                 }
            ],
            "rows":[
                {
                   "purchase_amount_sum":2052960,
                   "user_agent":0,
                   "date":"2017-06-02"
                },
                {
                   "purchase_amount_sum":6091040,
                   "user_agent":0,
                   "date":"2017-06-01"
                },
                {
                   "purchase_amount_sum":4122840,
                   "user_agent":1,
                   "date":"2017-06-02"
                },
                {
                   "purchase_amount_sum":12024040,
                   "user_agent":1,
                   "date":"2017-06-01"
                }
            ]
        },
        "query_hash":"48fc6c1a24b1b48a012542de33aeed75",
        "query":"SELECT user_agent, date, purchase_amount_sum\nFROM purchase_amount__daily\nWHERE TD_TIME_RANGE(TD_TIME_PARSE(date,"JST"), "2017-06-01 00:00:00", "2017-06-03 00:00:00", "JST")\nAND user_agent >= 0 AND user_agent <= 2\nORDER BY user_agent, date DESC;",
        "runtime":41.8847768306732
    }
}
```
