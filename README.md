# ssl-expiry-reminder

Sample SAM project for '[Python + AWS LambdaでSSL証明書の有効期限をチェックする](https://toranoana-lab.hatenablog.com/entry/2020/01/31/184136)'

## How to deploy

```
$ sam build
$ sam deploy --guided
```

## How to invoke the Lambda function locally

```
$ cp env.json.sample env.json  # and edit it
$ sam local invoke --env-vars env.json
```
