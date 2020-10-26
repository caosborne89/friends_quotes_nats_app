# Name of the project

Nats subscriber and publisher for publishing

## Requirements

* k3s v1.18 (used in development)

## Getting started
* Clone the repository (if you haven't already)

  ```shell
  git clone https://github.com/caosborne89/friends_quotes_nats_app.git
  ```
* cd into the project root

  ```shell
  cd friends_quotes_nats_app
  ```
* Run the following kubernetes commands (assumes `k3s kubectl` can be ran as just `kubectl`) from the project root
  * `kubectl apply -f https://raw.githubusercontent.com/nats-io/k8s/master/nats-server/single-server-nats.yml`
  * `kubectl apply -f friends-quote-app.yml`
  * `kubectl apply -f mysql.yml`
* After all the resources are created and all the containers are up you should be able ssh into the `mysql` pod and see the database being populated. The publisher is a Cronjob that runs every minute, so you should see a new quote being stored in the mysql database within that time interval.
  * Get the pod name - `kubectl get all`
  * ssh into the pod - `kubectl exec --stdin --tty <podname> -- /bin/bash`
  * Sign into mysql inside the container - `mysql -u root -ppassword`
  * Select the `nats_sub` database - `USE nats_sub;`
  * Select everything from the quotes table - `SELECT * quotes;`
  * You should see somethign similar to:
    ```mysql
    +----+--------------------------------+-------------------+---------------------+------------+---------------+
    | id | quote_str                      | friends_character | post_time           | ip         | nats_subject  |
    +----+--------------------------------+-------------------+---------------------+------------+---------------+
    |  1 | This is brand-new information! | Phoebe            | 2020-10-26 23:30:11 | 10.42.0.88 | friends_quote |
    |  2 | Unagi.                         | Ross              | 2020-10-26 23:31:11 | 10.42.0.88 | friends_quote |
    |  3 | I got off the plane.           | Rachel            | 2020-10-26 23:32:11 | 10.42.0.86 | friends_quote |
    |  4 | This is brand-new information! | Phoebe            | 2020-10-26 23:33:11 | 10.42.0.86 | friends_quote |
    |  5 | How you doin?                  | Joey              | 2020-10-26 23:34:12 | 10.42.0.86 | friends_quote |
    +----+--------------------------------+-------------------+---------------------+------------+---------------+
    5 rows in set (0.00 sec)
    ```

## Removing the application
* You can remove all the Kubernetes resources using the following command:
  ```shell
  kubectl delete configmap/nats-config service/nats statefulset.apps/nats cronjob.batch/app-friends-quotes-pub-deployment deployment.apps/app-friends-quotes-sub-deployment service/mysql persistentvolumeclaim/mysql-pv-claim deployment.apps/mysql configmap/mysql-migrations
  ```
## Things to note
* This project is currently not production ready. Next steps would be to better secure the database credentials using Kubernetes Secrets most likely.
* The docker files for the Friend quotes publisher and Friends quotes subscriber applications are stored in the `Docker file`. I'm not exactly familiar with Kubernetes local development workflow so it was more straight forward to push them to my DockerHub repo and pull them in Kubernetes. This is clearly not ideal, so a future feature would be to make it so you could develop the applications and test them in Kubernetes without first deploying to DockerHub. You can find the image repos at:
  * https://hub.docker.com/repository/docker/cao89/friends-quote-nats-sub
  * https://hub.docker.com/repository/docker/cao89/friends-quote-nats-pub
