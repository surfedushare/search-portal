import os

from invoke.tasks import task


@task(help={
    "input_file": "The .tab file that contains decompound definitions",
})
def create_decompound_dictionary(ctx, input_file):
    """
    Creates a Dutch decompound words dictionary that is suitable for ES from a .tab file.
    """
    output_file_path = os.path.join("elastic", "config", "decompound_word_list.nl.txt")
    tokens = set()
    with open(input_file, encoding="latin-1") as dictionary_input:
        for line in dictionary_input:
            word, compounds = line.split("\t")
            tokens.update([token.strip() + "\n" for token in compounds.split("+") if len(token.strip()) >= 3])
    with open(output_file_path, "w") as dictionary_output:
        dictionary_output.writelines(tokens)
    print("Created decompound dictionary file:", output_file_path)


@task(help={
    "decompound_file_path": "The decompound words dictionary to push to AWS",
    "package_id": "When updating the AWS ES package_id that should get updated"
})
def push_decompound_dictionary(ctx, decompound_file_path, package_id=None):
    """
    Creates or updates an AWS ES decompound word package based on a decompound dictionary
    """
    s3_bucket_name = "edushare-data"
    s3_keypath = "elastic/decompound_word_list.nl.txt"
    # Uploading to S3
    ctx.run(f"aws s3 cp {decompound_file_path} s3://{s3_bucket_name}/{s3_keypath}")
    # Associating the dictionary with a AWS ES package
    package_command = "create-package --package-name=decompound-words-list-nl --package-type=TXT-DICTIONARY"
    if package_id is not None:
        package_command = f"update-package --package-id={package_id}"
    ctx.run(
        f"aws es {package_command} "
        f"--package-source='S3BucketName={s3_bucket_name},S3Key={s3_keypath}'",
        echo=True, pty=True
    )
    print("AWS ES dictionary package created.")
    print("Do not forget to change the package identifier under the elastic_search.decompound_word_lists configuration")
