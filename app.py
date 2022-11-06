from flask import Flask,render_template,request
import redis
from tasks import count_words
from rq import Queue

r= redis.Redis(host='localhost',port=6379,db=0)
q = Queue(connection=r)


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/add_task',methods = ('GET','POST'))
def add_task():
    jobs = q.jobs
    message = None
    if request.method == "POST":
        url = request.form['url']
        tasks = q.enqueue(count_words,url)
        jobs = q.jobs
        q_length = len(q)
        message = f"The result is {tasks} and the jobs queued are {q_length}"
    return render_template("add_task.html",message= message, jobs = jobs)

if __name__ == "__main__":
    app.run(debug=True)