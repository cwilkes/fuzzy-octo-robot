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

for p in 1 2 3 4; do
  port="1000$p"
  dir="/src/redis/data$p"
  name="redis$p"
  boot2docker ssh "sudo mkdir -p $dir"
  docker run -d --name $name -v $dir:/data -p $port:6379 redis
done

redis_host=192.168.59.104
port=10001
file=~/rads_data/raw/2015-04-01/part-r-00000.gz

python post_cats_simple.py --host $redis_host --port $port $file

sites=$(redis-cli -h 192.168.59.104 -p 10001 smembers 'cat_site/ns:1:cat:17' | cut -d\" -f2)


partner_id=1
for p in 1 2 3 4; do 
  port="1000$p"
  redis-cli -h $redis_host -p $port sadd "perms/partner:$partner_id" $sites
  query_sha=$(redis-cli  -h $redis_host -p $port script load "$(cat pop_count_simple.lua)" )
  redis-cli -h $redis_host -p $port evalsha $query_sha 1 1 1 17
done

