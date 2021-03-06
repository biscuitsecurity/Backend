from backend.logic.utils import create_temp_incident
from backend.calculations.calculate import calculate_cosine
from backend.logic.questionGeneration import get_attribute_name, generate_question, generate_counter_question, \
    generate_mc_question
from backend.storage import mongo as db


def get_questions(ids, phase, categories):
    result = []
    topics_plural = ['sources', 'events', 'entities', 'impacts']
    for i, c in enumerate(topics_plural):
        copy_ids = set()
        for element in ids[c]:
            if element not in copy_ids:
                result.append(get({}, element, ids[c], i+1, copy_ids, phase, categories))

    return result


def get(result, attr_id, ids, topic_id, copy_ids, phase, categories):
    relations = db.get_relations(attr_id, topic_id)
    result['questions'] = []
    result['children'] = []
    # generic question get created (refinement + completion)
    question = generate_generic_question(attr_id, topic_id, phase, categories)
    result['questions'].append(question)
    copy_ids.add(attr_id)
    # completion
    if phase == 1:
        for r in relations:
            # load manually created questions from db
            temp = db.get_question(r['questionId'])
            for t in temp:
                q = generate_specific_question(t, r['attributeId'], topic_id)
                result['questions'].append(q)
        # load questions following attribute hierarchy
        for element in ids:
            if element[:-2] == attr_id:
                copy_ids.add(element)
                result['children'].append(get({}, element, ids, topic_id, copy_ids, phase, categories))
    # refinement
    else:
        for r in relations:
            # find existing counter questions for relation
            temp = db.get_question_counter(r['questionId'])
            # if counter questions exist
            if len(list(temp)) > 0:
                for t in temp:
                    q = generate_specific_question(t, r['attributeId'], topic_id)
                    result['questions'].append(q)
            # if counter question does not exist
            #else:
                # find non-counter question
                #q_positive = coll_que.find({'questionId': r['questionId']})
                # generate counter question for non-counter questions
                #for q in q_positive:
                    #q = generate_manual_counter_question(q, r['attributeId'], topic_id)
                    #result['questions'].append(q)
    if len(result['children']) == 0:
        del result['children']
    return result


def generate_generic_question(attr_id, topic_id, phase, categories):
    category = categories[topic_id-1]
    attribute = get_attribute_name(attr_id, category)
    if phase == 1:
        question = {'text': generate_question(attribute), 'answer': 0, 'questionId': 0, 'attrId': attr_id,
                    'topicId': topic_id}
    else:
        question = {'text': generate_counter_question(attribute), 'answer': 0, 'questionId': 0, 'attrId': attr_id,
                    'topicId': topic_id}
    if attr_id[:-2]:
        question['parentId'] = attr_id[:-2]
    return question


def generate_specific_question(q, attribute_id, topic_id):
    question = {'text': q['text'], 'answer': 0, 'questionId': q['questionId'], 'attrId': attribute_id,
                'topicId': topic_id}
    if attribute_id[:-2]:
        question['parentId'] = attribute_id[:-2]
    return question


def generate_manual_counter_question(q, attribute_id, topic_id):
    question = {'text': generate_mc_question(q['text']), 'answer': 0, 'questionId': q['questionId'],
                'attrId': attribute_id,
                'topicId': topic_id}
    if attribute_id[:-2]:
        question['parentId'] = attribute_id[:-2]
    return question


def execute_refinement(u, copy_nui, ref_norm_incidents, categories, s, ev, en, im, body):
    temp = {'title': copy_nui["title"], 'refId': copy_nui["refId"],
            'normSources': create_temp_incident(copy_nui['normSources'], s, body['answers'], 1),
            'normEvents': create_temp_incident(copy_nui['normEvents'], ev, body['answers'], 2),
            'normEntities': create_temp_incident(copy_nui['normEntities'], en, body['answers'], 3),
            'normImpacts': create_temp_incident(copy_nui['normImpacts'], im, body['answers'], 4)}
    question_ids = calculate_cosine(u, ref_norm_incidents, *categories, 2, temp)
    if len(question_ids) == 0:
        return {'id': u['refId'], 'questions': [], 'phase': 2}
    else:
        questions = get_questions(question_ids, 2, categories)
        question_response = {'id': u['refId'], 'questions': questions, 'phase': 2}
        return question_response


def execute_completion(user_incident, categories, norm_user_incident, norm_ref_incidents):
    question_ids = calculate_cosine(norm_user_incident, norm_ref_incidents, *categories, 1, None)
    questions = get_questions(question_ids, 1, categories)
    if len(question_ids) == 0:
        question_ids = calculate_cosine(norm_user_incident, norm_ref_incidents, *categories, 2, norm_user_incident)
        if len(question_ids) == 0:
            return {'id': norm_user_incident['refId'], 'questions': [], 'phase': 2}
        else:
            questions = get_questions(question_ids, 2, categories)
            question_response = {'id': norm_user_incident['refId'], 'questions': questions, 'phase': 2}
            return question_response
    else:
        question_response = {'id': user_incident['myId'], 'questions': questions, 'phase': 1}
    return question_response
