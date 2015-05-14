brew install redis
virtualenv-2.7 venv
. venv/bin/activate
pip install -r requirements.txt

# inserting
hashing_sha=$(redis-cli script load "$(cat bf.lua)" )
input_file=/tmp/part0.gz
python post_cats.py $hashing_sha $input_file

# create a partner
redis-cli sadd perms/partner:1 55	363	662	1124	1126	1407	2554	5163 5291	5766	7042	7459	7732	8779


# querying
query_sha=$(redis-cli script load "$(cat pop_count.lua)" )
# format of this is the first item is a "1" for "1 key to follow which is the partner id"
# then comes the partner id
# then ns, cat pairs

redis-cli evalsha $query_sha 1 1 1 1116 1 4844

response looks like: "raw=(1945,196434), estimate=(278,28342)"
where the first part is the raw bitcount of (and,or) the (1,1116) and (1,4844) nscats
the second is the population count using the bloomfilter equation

# docker

boot2docker upgrade
boot2docker init
boot2docker up
docker images
# should be nothing there

docker run -d --name redis -p 10000:6379 redis


 docker run -d --name redis1 -p 10001:6379 redis
 
