# Display final result
def print_last(relations, r):
    needed_relation=['per:schools_attended', 'per:employee_of', 'per:cities_of_residence','org:top_members/employees']
    print("============================= ALL RELATIONS FOR ", needed_relation[r-1], "(", len(relations), ") ==============================")
    for tuple_received in relations:
        print("Confidence: ", tuple_received[1], "             | Subject: ", tuple_received[2][0], "             | Object: ", tuple_received[3][0])
