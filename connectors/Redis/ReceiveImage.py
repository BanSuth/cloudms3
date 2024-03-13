import redis        # pip install redis
import io;

ip="35.203.54.228"
r = redis.Redis(host=ip, port=6379, db=1,password='sofe4630u')

value=r.get('fromKafka');

with open("./recieved.jpg", "wb") as f:
    f.write(value);
    
print('Image recieved, check ./recieved.jpg')
