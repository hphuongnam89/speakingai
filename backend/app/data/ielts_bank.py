import random

PART_1_TOPICS = [
    {
        "topic": "Work or Studies",
        "questions": [
            "Do you work or are you a student?",
            "What do you enjoy most about what you do?",
            "If you had the chance, would you change your current job or field of study?",
            "What kind of job would you like to do in the future?"
        ]
    },
    {
        "topic": "Hometown",
        "questions": [
            "Where is your hometown located?",
            "What do you like most about living there?",
            "Has your hometown changed much since you were a child?",
            "Would you like to live there in the future?"
        ]
    },
    {
        "topic": "Daily Routine & Free Time",
        "questions": [
            "What is your favorite time of the day and why?",
            "How do you usually spend your weekends?",
            "Do you prefer spending your free time alone or with other people?",
            "Has your free time routine changed compared to the past?"
        ]
    },
    {
        "topic": "Accommodation & Living Area",
        "questions": [
            "Do you live in a house or an apartment?",
            "What is your favorite room in your home and why?",
            "What kind of facilities are available in your neighborhood?",
            "What would you like to improve about your current home?"
        ]
    },
    {
        "topic": "Technology & Internet",
        "questions": [
            "How often do you use the internet for your daily tasks?",
            "What was the last app you downloaded on your phone?",
            "Do you think technology makes life simpler or more complicated?",
            "Can you imagine spending a full week without your mobile phone?"
        ]
    }
]

PART_2_CUE_CARDS = [
    {
        "id": "cue_card_1",
        "topic": "A Memorable Journey",
        "title": "Describe a memorable journey you went on.",
        "bullets": [
            "Where you went and how you traveled",
            "Who you traveled with",
            "What you did during the trip",
            "And explain why this journey was so memorable to you."
        ],
        "follow_up": "Do you still keep in touch with the people you met on that trip?",
        "part_3_questions": [
            "Why do you think international travel has become so popular in recent years?",
            "What are some negative environmental impacts of mass tourism?",
            "Do you believe virtual reality or online tours could ever replace real travel?",
            "How does tourism benefit local communities economically?"
        ]
    },
    {
        "id": "cue_card_2",
        "topic": "An Inspiring Person",
        "title": "Describe a person who taught you something useful.",
        "bullets": [
            "Who this person is",
            "What they taught you",
            "How they taught you this skill or lesson",
            "And explain why you found what they taught you to be so important."
        ],
        "follow_up": "Have you ever passed this skill or lesson on to someone else?",
        "part_3_questions": [
            "In your opinion, what makes someone an effective teacher or mentor?",
            "Should schools focus more on academic theory or practical real-world skills?",
            "Do you think older generations or younger generations learn more from each other nowadays?",
            "How has artificial intelligence changed the way people learn new knowledge?"
        ]
    },
    {
        "id": "cue_card_3",
        "topic": "An Important Decision",
        "title": "Describe an important decision you made in your life.",
        "bullets": [
            "What the decision was",
            "When and why you had to make it",
            "What options or alternatives you considered",
            "And explain how you felt after making this decision."
        ],
        "follow_up": "Would you make the same decision again if given the chance?",
        "part_3_questions": [
            "Why do some people find it difficult to make everyday decisions?",
            "Do you think young people should always seek advice from their parents when making career choices?",
            "How does having too many options impact a person's satisfaction with their decision?",
            "Can leaders make good decisions under high stress and limited information?"
        ]
    },
    {
        "id": "cue_card_4",
        "topic": "A Challenging Goal",
        "title": "Describe a challenging goal you achieved.",
        "bullets": [
            "What the goal was",
            "Why it was challenging for you",
            "How you planned and worked to achieve it",
            "And explain how you felt when you successfully achieved it."
        ],
        "follow_up": "Did achieving this goal inspire you to set bigger goals?",
        "part_3_questions": [
            "Why is setting long-term goals crucial for personal development?",
            "Do rewards and praise motivate people better than fear of failure?",
            "How can people stay disciplined when they face unexpected obstacles?",
            "Is ambition always a positive quality in modern society?"
        ]
    }
]

def get_random_part_1():
    return random.choice(PART_1_TOPICS)

def get_random_part_2():
    return random.choice(PART_2_CUE_CARDS)

def get_cue_card_by_id(cue_id: str):
    for c in PART_2_CUE_CARDS:
        if c["id"] == cue_id:
            return c
    return PART_2_CUE_CARDS[0]
