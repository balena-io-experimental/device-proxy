import random
from flask import Flask
app = Flask(__name__)

eight_ball_answers = [
    'It is certain.',
    'It is decidedly so.',
    'Without a doubt.',
    'Yes - definitely.',
    'You may rely on it.',
    'As I see it, yes.',
    'Most likely.',
    'Outlook good.',
    'Yes.',
    'Signs point to yes.',
    'Reply hazy, try again.',
    'Ask again later.',
    'Better not tell you now.',
    'Cannot predict now.',
    'Concentrate and ask again.',
    'Don\'t count on it.',
    'My reply is no.',
    'My sources say no.',
    'Outlook not so good.',
    'Very doubtful.',
    ]

@app.route('/')
def eight_ball():
    return f'🎱 {eight_ball_answers[random.randint(0, len(eight_ball_answers)-1)]}'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)