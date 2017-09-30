# Distrub
Distributed crawler using a series of Aiohttp servers, each running their own background task. When a request is sent to the dispatcher service, this fired of to the scraper service which simply grabs a page using a thread pool and then queues the results off to be sent to the parsing service. In turn the parsing server makes use of a process pool and extracts all the links which match the current domain being crawled.

```
#Expected input for dispatcher
{"urls" : [{"url": "http://edmundmartin.com"}]}
```
