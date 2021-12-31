import query
import scrape_url
import display

from w_bring_relations import extract_relations

needed_relation=['per:schools_attended', 'per:employee_of', 'per:cities_of_residence','org:top_members/employees']

# Take user input
print()
googlekey = str(input('Enter Google Search Key: ') or 'AIzaSyDFLI4iu83nBdeuUJkQTDH739PIyUqKuVM' )
enginekey = str(input('Enter Engine Key: ') or '3ad87265822f5240e')
r = int(input('Enter Relation Needed: ') or 2)
thresh = float((input('Enter Threshold Needed: ') or 0.7))
k = int(input('Enter Number of Tuples to Find: ') or 10)
q = str(input('Enter Query: ') or 'sundar pichai google')
print()
print('-------- PARAMETERS ---------')
print("Client Key       = ", googlekey)
print("Engine Key       = ", enginekey)
print("Relation         = ", needed_relation[r-1])
print("Threshold        = ", thresh)
print("Query            = ", q)
print("Number of Tuples = ", k)
print('-----------------------------')

perfect_relations = []
seen_urls = []

# Start iterating until k tuples are found.
iteration_number = 0
while len(perfect_relations) < k:
    iteration_number += 1
    relations_from_10=[]
    print('=========== Iteration: %s - Query: %s ===========' %(iteration_number, q))
    results = query.google_search(q, googlekey, enginekey)
    if any(past_url['url'] in seen_urls for past_url in results):
        print('Skipping the following already seen urls: ')
        print([past_url['url'] for past_url in results if past_url['url'] in seen_urls])
        results = [past_url for past_url in results if past_url['url'] not in seen_urls]
        print('---------------------------------------------')
        seen_urls += [past_url['url'] for past_url in results]

    # Scrape the results
    scrape_url.fetch_content(results)

    # Limit number of characters to 20000
    for x in results:
        x['content']=x['content'][:20000] if len(x['content']) > 20000 else x['content']
    all_content = []
    for x in results:
        all_content.append(x['content'])

    # Extract relations
    relations_from_10 = extract_relations(all_content, thresh, perfect_relations, r, results)

    if len(relations_from_10) == 0:
        print('Zero relations were found from the next 10 fetched documents, stopping search')
        print('Number of valid relations found =', len(perfect_relations))
        display.print_last(perfect_relations, r)
        print("======== Total Iterations :", iteration_number)
        exit()
    for each in relations_from_10:
        perfect_relations.append(each)

    # Sort the extracted relations in decreasing order of confidence scores
    perfect_relations = sorted(perfect_relations, key=lambda x: x[1], reverse=True)
    if len(perfect_relations) >= k:
        print('Required number of relations were found, stopping search')
        print('Number of valid relations found =', len(perfect_relations))
        #perfect_relations = perfect_relations[0:k]
        display.print_last(perfect_relations, r)
    else:
        q = ''
        q = relations_from_10[0][2][0] + " " + relations_from_10[0][3][0]
        display.print_last(perfect_relations, r)
print("======== Total Iterations :", iteration_number)