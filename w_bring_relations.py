import spacy
from spanbert import SpanBERT
from spacy_help_functions import get_entities, create_entity_pairs

# TODO: filter entities of interest based on target relation
entities_of_interest = ["ORGANIZATION", "PERSON", "LOCATION", "CITY", "STATE_OR_PROVINCE", "COUNTRY"]

# Load spacy model
nlp = spacy.load("en_core_web_lg")

# Load pre-trained SpanBERT model
spanbert = SpanBERT("./pretrained_spanbert")

relation_preds=[]

def extract_relations(r_list, thresh, perfect_relations, relation, results):
	final_ans = []
	c = 0
	url_count = 1
	for raw_text in r_list:
		print("URL ( ", url_count, " / 10 ): ", results[url_count-1]['url'])
		print("\tFetching text from URL...")
		print("\tWebpage Length (number of characters): ", len(raw_text))
		print("\tAnnotating the webpage using SpaCy")
		print()
		url_count += 1
		from_this_website=0
		doc = nlp(raw_text)
		total = 0
		se_count = 0
		for s in doc.sents:
			total = total + 1
		print("\tExtracted ", total, " sentences. Processing each sentence one by one to check for presence of right pair of named entity types; if so, will run the second pipeline ...")
		good_sentences = 0
		for sentence in doc.sents:
			se_count = se_count + 1
			if int(se_count) % 5 == 0:
				print('\tProcessed ' + str(se_count) + '/' + str(total) + ' sentences')
			relation_preds=[]
			ents = get_entities(sentence, entities_of_interest)

			# create entity pairs
			candidate_pairs = []
			sentence_entity_pairs = create_entity_pairs(sentence, entities_of_interest)

			i = 0

			for ep in sentence_entity_pairs:
				i = i + 1

				# TODO: keep subject-object pairs of the right type for the target relation (e.g., Person:Organization for the "Work_For" relation)
				if ep[1][1] == 'PERSON' and ep[2][1] == 'ORGANIZATION':
					candidate_pairs.append({"tokens": ep[0], "subj": ep[1], "obj": ep[2]})  # e1=Subject, e2=Object
				if ep[2][1] == 'PERSON' and ep[1][1] == 'ORGANIZATION':
					candidate_pairs.append({"tokens": ep[0], "subj": ep[1], "obj": ep[2]})
				if ep[1][1] == 'PERSON' and ep[2][1] in ["LOCATION", "CITY", "STATE_OR_PROVINCE", "COUNTRY"]:
					candidate_pairs.append({"tokens": ep[0], "subj": ep[1], "obj": ep[2]})  # e1=Object, e2=Subject

			candidate_pairs = [p for p in candidate_pairs if p["subj"][1] in ["PERSON", "ORGANIZATION"]]
			candidate_pairs = [p for p in candidate_pairs if p["obj"][1] in ["ORGANIZATION", "PERSON", "LOCATION", "CITY", "STATE_OR_PROVINCE", "COUNTRY"]]
			if len(candidate_pairs) == 0:
				continue

			# Get Predictions: list of (relation, confidence) pairs
			if len(candidate_pairs) != 0:
				relation_preds = spanbert.predict(candidate_pairs)

			if len(relation_preds) == 0:
				continue

			good_sentences = good_sentences + 1
			for ex, pred in list(zip(candidate_pairs, relation_preds)):
				tbr_small = []
				tbr_big=[]
				needed_relation=['per:schools_attended', 'per:employee_of', 'per:cities_of_residence','org:top_members/employees']
				if pred[0] == needed_relation[relation-1]:
					s = sentence
					conf = pred[1]
					sb = ex['subj']
					ob = ex['obj']
					r = pred[0]
					tuple_sent = (s, conf, sb, ob, r)
					print("\t\t========== EXTRACTED RELATION ==========")
					print("\t\tSentence = ", tuple_sent[0])
					print("\t\tConfidence = ", tuple_sent[1])
					print("\t\tSubject = ", tuple_sent[2][0])
					print("\t\tObject = ", tuple_sent[3][0])
					print("\t\tRelation = ", tuple_sent[4])
					print('\n')
					flag = 0
					if tuple_sent[1]<thresh:
						print('\t\tConfidence less than required threshold. Ignoring this')
						continue

					for f in final_ans:
						if flag == 0:
							if f[2] == sb and f[3] == ob and f[4] == r:
								flag = 1
								if f[1] < conf:
									tbr_small.append(f)
									final_ans.append(tuple_sent)
									print('\t\tAdding relation to final set')
									from_this_website = from_this_website + 1
									print('\n')
								else:
									print('\t\tDuplicate relation with confidence not greater than that of the one already present, skipping')
									print('\n')
									continue
					for tbr in tbr_small:
						final_ans.remove(tbr)

					if len(perfect_relations)!=0:
						for f in perfect_relations:
							if flag == 0:
								if f[2] == sb and f[3] == ob and f[4] == r:
									flag = 1
									if f[1] < conf:
										tbr_big.append(f)
										final_ans.append(tuple_sent)
										print('\t\tAdding relation to final set')
										from_this_website=from_this_website+1
										print('\n')
									else:
										print('\t\tDuplicate relation with confidence not greater than that of the one already present, skipping')
										print('\n')

					for tbr in tbr_big:
						perfect_relations.remove(tbr)
					if flag == 0 and tuple_sent[1] >= thresh:
						final_ans.append(tuple_sent)
						print('\t\tAdding relation to final set')
						from_this_website=from_this_website+1
						print('\n')
		print("\tExtracted relations for", good_sentences, "out of total", total, "sentences")
		if len(perfect_relations) == 0:
			print("\tFrom this website, the number of relations we got is:", from_this_website, "(Overall: ", len(final_ans), ")")
		else:
			res = len(perfect_relations) + len(final_ans)
			print("\tFrom this website, the number of relations we got is:", from_this_website, "(Overall: ", res, ")")

	final_ans = sorted(final_ans, key=lambda x: x[1], reverse=True)
	return final_ans
