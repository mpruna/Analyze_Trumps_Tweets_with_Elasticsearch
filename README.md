# To Do List

- [X] Created a docker-compose elk/(elastic/kibana) stack
- [X] Working Jupyter nb
- [X] Export enviroment.yml
- [X] Setup a high level plan to orchestrate the pipeline into Elasticsearch
- [X] Create an S3 bucket and upload files to it
- [X] Create an S3 python pipeline

### Storyline

2017 Presidential election was a strange turn of events. Aside from the traditional Republican/Democrats debate, the whole context seemed a little bit dubious. While seeking advice from a friend regarding Data Science, or better yet how to learn Data Science, he mentioned that I could do a tweeter analysis. I must admit that sounded interesting. Also, remember clearly that at that time he said something about technologies which seemed voodoo-like Docker, Elacticsearch, NoSQL DBs, I bearly knew python back then. Needless to say, an opportunity arose for me to an Analysis of Trump's tweeter, and also use these technologies. Within this blog post, I touch on some of the vital Data Science project life cycles. From a technological standpoint, most likely in a real-world scenario, the dataset must be stored in a cloud environment. An ETL pipeline must be created from our storage medium to the backend DB. In almost all Data Science/ML projects data must be curated, manipulated. Text analysis can have multiple benefits one would be scoring "Curriculum Vitaes.", or possibly, in this case, provide a model that can forecast how Trumps Tweets can influence the market. At the end of the Blog Post, I would also point out some areas of improvement

For this mini-project, I will use:

* Docker/docker-compose(container-based "virtualisation technology"/orchestration)
* Elasticsearch/Kibana
* Python ETL

Technology breakdown

Docker is a "container-based" operating-system-level virtualization. Within Docker, applications are built on containers based on specific images. One of the benefits of using docker technology is that it is "lightweight." In comparison to the traditional VM technologies, it does doesn't need a guest operating system and access to host resources is not done through a Hypervisor, Docker runs a discrete process and gets from the host all the resources it needs. Docker is built upon layers, and the top layer represents the container actually, the application we want to run will runtime executable and environment variables. Another benefit of using Docker is that you can deploy and use applications in minutes. As orchestration, we use Docker compose, where we define all the services and interactions between them.

Elasticsearch is a NoSQL database ideal for log parsing and text analysis. NoSQL databases are useful for storing unstructured data. What's needed is the data definition or the index schema. For those used with traditional SQL DBS find below the analogy

### Comparision
SQL DB | NoSQL DB
| --- | --- |
Indices | Databases |
Types | Tables |
Rows | Documents |
Columns | Fields |

Additionally, Elasticsearch comes with a feature reach front end Kibana, which allows us to build useful visualizations and aggregated queries in just a few clicks, there are a wealth of features including machine learning modules, helpful developer APIs.

Dataset is available here, and also there is a GitHub repo where Trump's tweeter history is available.
Data Science workflow

A Data Science project has several parts, and each step influences the next one, the ultimate goal is to provide an answer/model which responds to a particular question, it should have real-world applicability. However, in this project, I will only do exploratory data analysis and will not focus on a machine learning forecasting algorithm. In a real-world scenario where datasets are above 25 GB, and data is diverse, you also need to have a large storage medium. For this, I will use AWS S3 (Simple Storage Solution). Also, a pipeline/an ETL pipeline must be created from the S3 to our Elasticseach DB. There are many technologies in the market, such as Kafka, and Elastic stack comes with its Logstash. However for I will use for the moment jupyter-notebook