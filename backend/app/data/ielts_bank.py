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
    },
    {
        "topic": "Food & Cooking",
        "questions": [
            "What kinds of food do you most enjoy eating?",
            "Do you prefer cooking at home or eating out at restaurants?",
            "What is a traditional dish from your country that you recommend to foreigners?",
            "Has your diet changed in any way over the past few years?"
        ]
    },
    {
        "topic": "Travel & Holidays",
        "questions": [
            "What was the most memorable holiday trip you have ever taken?",
            "Do you prefer traveling alone or with a group of friends or family?",
            "Which foreign country or city would you most like to visit in the future?",
            "What do you think is the best way to travel long distances?"
        ]
    },
    {
        "topic": "Weather & Climate",
        "questions": [
            "What kind of weather do you like best?",
            "Does the weather affect your mood or daily productivity?",
            "What is the weather usually like in your country during the winter?",
            "Do you think climate change is affecting the seasons in your hometown?"
        ]
    },
    {
        "topic": "Music & Entertainment",
        "questions": [
            "What genre of music do you listen to when you want to relax?",
            "Have you ever attended a live concert or music performance?",
            "Do you play any musical instruments or wish you could play one?",
            "How has the way people listen to music changed compared to the past?"
        ]
    },
    {
        "topic": "Sports & Physical Exercise",
        "questions": [
            "What kinds of sports or physical activities do you enjoy?",
            "Did you play any sports when you were in primary or secondary school?",
            "Do you prefer watching sports live in a stadium or on television?",
            "Why is regular physical exercise so important for people nowadays?"
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
    },
    {
        "id": "cue_card_5",
        "topic": "A Useful Device or Technology",
        "title": "Describe a piece of electronic equipment or technology that you find useful.",
        "bullets": [
            "What the device is and how often you use it",
            "When and why you got it",
            "What features you find most helpful",
            "And explain how your daily life would be affected if you didn't have it."
        ],
        "follow_up": "Do you consider yourself an early adopter of new technology?",
        "part_3_questions": [
            "How has reliance on smartphones altered interpersonal communication?",
            "Will artificial intelligence replace intellectual professions in the near future?",
            "What challenges do senior citizens encounter when adapting to new tech devices?",
            "Should children have restricted screen time during their formative years?"
        ]
    },
    {
        "id": "cue_card_6",
        "topic": "An Environmental Concern",
        "title": "Describe an environmental problem in your local city or country.",
        "bullets": [
            "What the problem is and where it occurs",
            "What causes this issue",
            "How it affects local residents and wildlife",
            "And explain what measures can be taken to solve or mitigate it."
        ],
        "follow_up": "Are people in your community actively participating in environmental cleanup?",
        "part_3_questions": [
            "Who bears greater responsibility for combating pollution: governments or individuals?",
            "Can economic development and environmental protection realistically coexist?",
            "Why do many people still hesitate to adopt zero-waste and recycling lifestyles?",
            "What role should schools play in educating younger generations about ecology?"
        ]
    }
]

DAILY_TOPICS = [
    {
        "id": "daily_1",
        "topic": "Daily Routine & Productivity",
        "titleVi": "Nhịp sinh hoạt & Năng suất làm việc",
        "opening": "How do you usually start your morning, and what is your favorite part of the day?"
    },
    {
        "id": "daily_2",
        "topic": "Coffee, Tea & Cafe Culture",
        "titleVi": "Văn hóa cà phê & Không gian thư giãn",
        "opening": "Do you prefer drinking coffee or tea, and what kind of atmosphere do you look for in a cafe?"
    },
    {
        "id": "daily_3",
        "topic": "Weekend Plans & Unwinding",
        "titleVi": "Kế hoạch cuối tuần & Xả stress",
        "opening": "What is your ideal way to recharge your energy after a demanding week?"
    },
    {
        "id": "daily_4",
        "topic": "Films, Series & Books",
        "titleVi": "Phim ảnh, Sách truyện & Giải trí",
        "opening": "What was the most engaging movie or book you enjoyed recently, and why did it stand out?"
    },
    {
        "id": "daily_5",
        "topic": "Future Ambitions & Bucket List",
        "titleVi": "Mục tiêu tương lai & Trải nghiệm mơ ước",
        "opening": "If you could master any new skill or visit any destination in the next year, what would you choose?"
    }
]

def get_topics_catalog():
    return {
        "part1": PART_1_TOPICS,
        "part2": PART_2_CUE_CARDS,
        "daily": DAILY_TOPICS
    }

def find_part_1_by_topic(name: str):
    if not name:
        return None
    name_clean = name.strip().lower()
    for t in PART_1_TOPICS:
        if name_clean in t["topic"].lower() or t["topic"].lower() in name_clean:
            return t
    return None

def find_cue_card_by_topic(name_or_id: str):
    if not name_or_id:
        return None
    q = name_or_id.strip().lower()
    for c in PART_2_CUE_CARDS:
        if c["id"].lower() == q or q in c["topic"].lower() or c["topic"].lower() in q or q in c["title"].lower():
            return c
    return None

def get_random_part_1():
    return random.choice(PART_1_TOPICS)

def get_random_part_2():
    return random.choice(PART_2_CUE_CARDS)

def get_cue_card_by_id(cue_id: str):
    for c in PART_2_CUE_CARDS:
        if c["id"] == cue_id:
            return c
    return PART_2_CUE_CARDS[0]
