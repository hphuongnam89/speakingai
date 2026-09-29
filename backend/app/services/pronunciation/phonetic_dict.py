"""
Phonetic dictionary and G2P (Grapheme-to-Phoneme) engine.
Provides IPA transcriptions, syllable breakdowns, stress patterns, and phonetic tips.
"""

# Core dictionary of frequently used IELTS & conversational vocabulary with accurate IPA and syllables
COMMON_IPA_DICT = {
    # Academic & Topic vocabulary
    "enjoyed": ("/ɪnˈdʒɔɪd/", ["en", "joyed"], 1, "Focus on the voiced ending /d/ sound without adding an extra vowel."),
    "technology": ("/tɛkˈnɒlədʒi/", ["tech", "nol", "o", "gy"], 1, "Stress the second syllable: tech-NOL-o-gy."),
    "environment": ("/ɪnˈvaɪrənmənt/", ["en", "vi", "ron", "ment"], 1, "Stress the second syllable /vaɪ/. Pronounce the 'n' before 'ment' clearly."),
    "development": ("/dɪˈvɛləpmənt/", ["de", "vel", "op", "ment"], 1, "Stress is on 'vel': di-VEL-up-ment."),
    "government": ("/ˈɡʌvənmənt/", ["gov", "ern", "ment"], 0, "First syllable stressed: GOV-ern-ment."),
    "important": ("/ɪmˈpɔːtnt/", ["im", "por", "tant"], 1, "Stress the middle syllable: im-POR-tant."),
    "education": ("/ˌɛdʒʊˈkeɪʃn/", ["ed", "u", "ca", "tion"], 2, "Main stress is on 'ca': ed-ju-CAY-shun."),
    "opportunity": ("/ˌɒpəˈtjuːnəti/", ["op", "por", "tu", "ni", "ty"], 2, "Stress on 'tu': op-por-TU-ni-ty."),
    "experience": ("/ɪkˈspɪəriəns/", ["ex", "pe", "ri", "ence"], 1, "Stress 'pe': ex-PEER-ee-uns."),
    "society": ("/səˈsaɪəti/", ["so", "ci", "e", "ty"], 1, "Second syllable is stressed: suh-SY-uh-tee."),
    "comfortable": ("/ˈkʌmftəbl/", ["com", "fort", "a", "ble"], 0, "Notice it is 3 syllables in natural speech: KUMF-tuh-bl."),
    "vegetable": ("/ˈvɛdʒtəbl/", ["veg", "e", "ta", "ble"], 0, "Pronounced VEJ-tuh-bl, avoid saying 've-ge-ta-ble'."),
    "interesting": ("/ˈɪntrəstɪŋ/", ["in", "ter", "est", "ing"], 0, "Stress the first syllable: IN-truh-sting."),
    "especially": ("/ɪˈspɛʃəli/", ["es", "pe", "cial", "ly"], 1, "Stress 'pe': eh-SPESH-uh-lee. Avoid adding an initial /e/ sound."),
    "specifically": ("/spəˈsɪfɪkli/", ["spe", "cif", "i", "cal", "ly"], 1, "Stress 'cif': spuh-SIF-ik-lee."),
    "particular": ("/pəˈtɪkjələ/", ["par", "tic", "u", "lar"], 1, "Stress 'tic': puh-TIK-yuh-luh."),
    "significantly": ("/sɪɡˈnɪfɪkəntli/", ["sig", "nif", "i", "cant", "ly"], 1, "Stress 'nif': sig-NIF-ih-kunt-lee."),
    "consequence": ("/ˈkɒnsɪkwəns/", ["con", "se", "quence"], 0, "Stress the first syllable: KON-sih-kwuns."),
    "advantage": ("/ədˈvɑːntɪdʒ/", ["ad", "van", "tage"], 1, "Stress 'van': ud-VAHN-tij."),
    "disadvantage": ("/ˌdɪsədˈvɑːntɪdʒ/", ["dis", "ad", "van", "tage"], 2, "Stress 'van': dis-ud-VAHN-tij."),
    "influence": ("/ˈɪnfluəns/", ["in", "flu", "ence"], 0, "Stress first syllable: IN-floo-unce."),
    "beneficial": ("/ˌbɛnɪˈfɪʃl/", ["ben", "e", "fi", "cial"], 2, "Stress 'fi': ben-eh-FISH-ul."),
    "challenge": ("/ˈtʃælɪndʒ/", ["chal", "lenge"], 0, "Starts with /tʃ/ and ends with soft /dʒ/."),
    "achieve": ("/əˈtʃiːv/", ["a", "chieve"], 1, "Second syllable stressed with long /iː/ and voiced /v/."),
    "pronounce": ("/prəˈnaʊns/", ["pro", "nounce"], 1, "Contains /aʊ/ diphthong like 'now'."),
    "pronunciation": ("/prəˌnʌnsiˈeɪʃn/", ["pro", "nun", "ci", "a", "tion"], 3, "Notice 'nun' /nʌn/, NOT 'noun'! Main stress on 'a'."),
    "vocabulary": ("/vəˈkæbjələri/", ["vo", "cab", "u", "la", "ry"], 1, "Stress on 'cab': vuh-KAB-yuh-luh-ree."),
    "grammar": ("/ˈɡræmə/", ["gram", "mar"], 0, "First syllable stressed with short /æ/."),
    "fluency": ("/ˈfluːənsi/", ["flu", "en", "cy"], 0, "Stress first syllable with long /uː/."),
    "coherence": ("/kəʊˈhɪərəns/", ["co", "her", "ence"], 1, "Stress 'her': koh-HEER-unce."),
    "candidate": ("/ˈkændɪdət/", ["can", "di", "date"], 0, "Stress first syllable: KAN-dih-duht."),
    "examiner": ("/ɪɡˈzæmɪnə/", ["ex", "am", "i", "ner"], 1, "Stress 'am': ig-ZAM-in-uh."),
    "perspective": ("/pəˈspɛktɪv/", ["per", "spec", "tive"], 1, "Stress 'spec': pur-SPEK-tiv."),
    "individual": ("/ˌɪndɪˈvɪdʒuəl/", ["in", "di", "vid", "u", "al"], 2, "Stress 'vid': in-dih-VID-joo-ul."),
    "communication": ("/kəˌmjuːnɪˈkeɪʃn/", ["com", "mu", "ni", "ca", "tion"], 3, "Main stress on 'ca': kuh-myoo-nih-KAY-shun."),
    "culture": ("/ˈkʌltʃə/", ["cul", "ture"], 0, "First syllable /kʌl/, ends with /tʃə/."),
    "tradition": ("/trəˈdɪʃn/", ["tra", "di", "tion"], 1, "Stress 'di': truh-DISH-un."),
    "memory": ("/ˈmɛməri/", ["mem", "o", "ry"], 0, "Stress first syllable: MEM-uh-ree."),
    "memorable": ("/ˈmɛmərəbl/", ["mem", "o", "ra", "ble"], 0, "Stress on 'mem': MEM-ruh-bl."),
    "journey": ("/ˈdʒɜːni/", ["jour", "ney"], 0, "First syllable /dʒɜː/, ends with /ni/."),
    "delicious": ("/dɪˈlɪʃəs/", ["de", "li", "cious"], 1, "Stress 'li': dih-LISH-us."),
    "coastal": ("/ˈkəʊstl/", ["coast", "al"], 0, "Diphthong /əʊ/ as in 'boat'."),
    "beautiful": ("/ˈbjuːtɪfl/", ["beau", "ti", "ful"], 0, "Starts with /bjuː/ like 'view'."),
    "wonderful": ("/ˈwʌndəfl/", ["won", "der", "ful"], 0, "First syllable /wʌn/."),
    "actually": ("/ˈæktʃuəli/", ["ac", "tu", "al", "ly"], 0, "Stress on 'ac': AK-choo-uh-lee."),
    "probably": ("/ˈprɒbəbli/", ["prob", "a", "bly"], 0, "Three syllables: PROB-uh-blee."),
    "definitely": ("/ˈdɛfɪnətli/", ["def", "i", "nite", "ly"], 0, "Stress 'def': DEF-ih-nut-lee."),
    "thought": ("/θɔːt/", ["thought"], 0, "Voiceless /θ/ sound; ensure tongue is between teeth."),
    "through": ("/θruː/", ["through"], 0, "Voiceless /θ/ followed by /r/ and long /uː/."),
    "although": ("/ɔːlˈðəʊ/", ["al", "though"], 1, "Voiced /ð/ in the second syllable."),
    "weather": ("/ˈwɛðə/", ["weath", "er"], 0, "Voiced /ð/ sound in the middle."),
    "together": ("/təˈɡɛðə/", ["to", "geth", "er"], 1, "Voiced /ð/ sound with stress on 'geth'."),
    "colleague": ("/ˈkɒliːɡ/", ["col", "league"], 0, "Stress 'col': KOL-eeg. Hard /ɡ/ at the end."),
    "university": ("/ˌjuːnɪˈvɜːsəti/", ["u", "ni", "ver", "si", "ty"], 2, "Main stress on 'ver': yoo-nih-VER-suh-tee."),
}

# Rule-based vowel & consonant mappings for general English fallback
PHONEME_RULES = [
    ("tion", "ʃn"),
    ("sion", "ʒn"),
    ("cious", "ʃəs"),
    ("tious", "ʃəs"),
    ("ought", "ɔːt"),
    ("aught", "ɔːt"),
    ("ight", "aɪt"),
    ("ough", "oʊ"),
    ("tch", "tʃ"),
    ("ch", "tʃ"),
    ("sh", "ʃ"),
    ("th", "θ"),
    ("ph", "f"),
    ("wh", "w"),
    ("ck", "k"),
    ("qu", "kw"),
    ("ee", "iː"),
    ("ea", "iː"),
    ("oo", "uː"),
    ("ou", "aʊ"),
    ("ow", "aʊ"),
    ("ai", "eɪ"),
    ("ay", "eɪ"),
    ("oi", "ɔɪ"),
    ("oy", "ɔɪ"),
    ("ar", "ɑːr"),
    ("or", "ɔːr"),
    ("er", "ɜːr"),
    ("ir", "ɜːr"),
    ("ur", "ɜːr"),
]

def split_into_syllables(word: str) -> list[str]:
    """Basic English syllable estimator using vowel clusters."""
    clean = word.lower().strip(".,!?:;\"'()[]")
    if not clean:
        return [word]
    if len(clean) <= 3:
        return [clean]

    vowels = "aeiouy"
    syllables = []
    current = ""
    in_vowel = False

    for i, ch in enumerate(clean):
        current += ch
        if ch in vowels:
            in_vowel = True
        elif in_vowel:
            # Check if this consonant marks syllable boundary
            if i + 1 < len(clean) and clean[i + 1] in vowels:
                syllables.append(current[:-1])
                current = ch
                in_vowel = False

    if current:
        if syllables and len(current) == 1 and current not in vowels:
            syllables[-1] += current
        else:
            syllables.append(current)

    return syllables if syllables else [clean]

def estimate_rule_based_ipa(word: str) -> str:
    """Generate an approximate IPA transcription using phonetic spelling rules."""
    w = word.lower().strip(".,!?:;\"'()[]")
    if not w:
        return ""
    
    ipa = w
    for pattern, repl in PHONEME_RULES:
        ipa = ipa.replace(pattern, repl)
        
    # Standard consonants & vowels
    ipa = ipa.replace("c", "k")
    ipa = ipa.replace("j", "dʒ")
    ipa = ipa.replace("x", "ks")
    
    return f"/{ipa}/"

def get_phonetic_info(word: str) -> dict:
    """
    Looks up phonetic info for a word.
    Returns:
        ipa: Expected IPA pronunciation
        syllables: Syllable breakdown
        stress_index: 0-indexed syllable with primary stress
        feedback: Specific pronunciation hint
    """
    clean = word.lower().strip(".,!?:;\"'()[]")
    
    if clean in COMMON_IPA_DICT:
        ipa, syllables, stress, feedback = COMMON_IPA_DICT[clean]
        return {
            "word": clean,
            "expected_ipa": ipa,
            "syllables": syllables,
            "stress_index": stress,
            "feedback": feedback
        }

    # Fallback to rule-based approximation
    syllables = split_into_syllables(clean)
    stress_idx = 0 if len(syllables) <= 2 else 1
    ipa = estimate_rule_based_ipa(clean)
    
    # Generic phonetic guidance based on tricky endings
    hint = "Enunciate clearly and maintain vocal projection."
    if clean.endswith("ed"):
        hint = "Check the past tense ending (/t/, /d/, or /ɪd/)."
    elif clean.endswith("s") or clean.endswith("es"):
        hint = "Pronounce the final /s/ or /z/ sound distinctly."
    elif "th" in clean:
        hint = "Place tongue slightly between teeth for the 'th' sound."
    elif len(syllables) > 2:
        hint = f"Place main stress on syllable '{syllables[stress_idx].upper()}'."

    return {
        "word": clean,
        "expected_ipa": ipa,
        "syllables": syllables,
        "stress_index": stress_idx,
        "feedback": hint
    }
