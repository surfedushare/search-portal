import os
import json
from collections import defaultdict
from invoke import task, Exit
from opensearchpy import OpenSearch
from opensearchpy.helpers import streaming_bulk

from commands.opensearch.utils import get_remote_search_client
from search_client import SearchClient
from search_client.constants import LANGUAGES, DocumentTypes
from search_client.open_search.configuration import create_open_search_index_configuration


@task(help={
    "input_file": "The .tab file that contains decompound definitions",
})
def create_decompound_dictionary(ctx, input_file):
    """
    Creates a Dutch decompound words dictionary that is suitable for ES from a .tab file.
    """
    output_file_path = os.path.join("opensearch", "config", "decompound_word_list.nl.txt")
    tokens = set()
    with open(input_file, encoding="latin-1") as dictionary_input:
        for line in dictionary_input:
            word, compounds = line.split("\t")
            tokens.update([token.strip() + "\n" for token in compounds.split("+") if len(token.strip()) >= 3])
    with open(output_file_path, "w") as dictionary_output:
        dictionary_output.writelines(tokens)
    print("Created decompound dictionary file:", output_file_path)


@task(help={
    "decompound_file_path": "The decompound words dictionary to push to AWS"
})
def push_decompound_dictionary(ctx, decompound_file_path):
    """
    Creates or updates an AWS ES decompound word package based on a decompound dictionary
    """
    profile_env = f"AWS_PROFILE={ctx.config.aws.profile_name}"
    s3_bucket_name = ctx.config.aws.harvest_content_bucket
    s3_keypath = "opensearch/decompound_word_list.nl.txt"
    # Uploading to S3
    ctx.run(
        f"{profile_env} aws s3 cp {decompound_file_path} s3://{s3_bucket_name}/{s3_keypath}"
    )
    # Now we're associating the dictionary with a AWS ES package
    # First we check for existing packages
    package_id = None
    package_descriptions = ctx.run(
        "aws es describe-packages --filter='Name=PackageName,Value=decompound-words-list-nl'"
    )
    package_details_list = json.loads(package_descriptions.stdout).get("PackageDetailsList", [])
    if len(package_details_list):
        package_id = package_details_list[0]["PackageID"]
    # Then we create or update the package with the given decompound dictionary
    package_command = "create-package --package-name=decompound-words-list-nl --package-type=TXT-DICTIONARY"
    if package_id is not None:
        package_command = f"update-package --package-id={package_id}"
    ctx.run(
        f"{profile_env} aws es {package_command} "
        f"--package-source='S3BucketName={s3_bucket_name},S3Key={s3_keypath}'",
        echo=True, pty=True
    )
    # And last but not least we associate the package with the ES domain
    ctx.run(
        f"{profile_env} aws es associate-package "
        f"--package-id={package_id} --domain-name={ctx.config.open_search.domain_name}",
        echo=True, pty=True
    )
    print("AWS ES dictionary package processed.")
    print("Do not forget to set the package identifier under the open_search.decompound_word_lists configuration")


@task
def push_indices_template(ctx):
    """
    Creates or updates index templates to create indices with correct settings
    """
    client = get_remote_search_client(ctx)
    client.indices.put_template("basic-settings", body={
        "index_patterns": [
            "harvest-logs*", "document-logs*", "service-logs*", "search-results*", "harvest-results*", "api"
        ],
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }
    })


@task
def recreate_test_indices(ctx):
    if ctx.config.aws.is_aws:
        raise Exit("Refusing the recreate indices on AWS environments with this development command")
    client = OpenSearch(f"{ctx.config.open_search.protocol}://{ctx.config.open_search.host}")
    with open(os.path.join("commands", "opensearch", "data", "test.json")) as json_file:
        documents = json.load(json_file)
    documents_by_language = defaultdict(list)
    for doc in documents:
        language = doc["language"] if doc["language"] in LANGUAGES else "unk"
        documents_by_language[language].append(doc)
    for language in LANGUAGES:
        index = f"{ctx.config.open_search.alias_prefix}-{language}"
        if client.indices.exists(index):
            print(f"Deleting index {index}")
            client.indices.delete(index=index)
        print(f"Creating index {index}")
        client.indices.create(
            index=index,
            body=create_open_search_index_configuration(language, DocumentTypes.LEARNING_MATERIAL)
        )
        print("Document count:", len(documents_by_language[language]))
        for is_ok, result in streaming_bulk(client, documents_by_language[language], index=index, chunk_size=100,
                                            yield_ok=False, raise_on_error=True, request_timeout=60):
            if not is_ok:
                print(result)
