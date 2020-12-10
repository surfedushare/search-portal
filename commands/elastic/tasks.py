import os

from invoke.tasks import task


@task
def create_decompound_dictionary(ctx, input_file):
    output_file_path = os.path.join("elastic", "config", "decompound_word_list.nl.txt")
    tokens = set()
    with open(input_file, encoding="latin-1") as dictionary_input:
        for line in dictionary_input:
            word, compounds = line.split("\t")
            tokens.update([token.strip() + "\n" for token in compounds.split("+") if len(token.strip()) >= 3])
    with open(output_file_path, "w") as dictionary_output:
        dictionary_output.writelines(tokens)
    print("Created decompound dictionary file:", output_file_path)


@task
def push_decompound_dictionary(ctx, decompound_file_path):
    ctx.run(f"aws s3 cp {decompound_file_path} s3://edushare-data/elastic/decompound_word_list.nl.txt")
