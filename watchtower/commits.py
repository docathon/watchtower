

def is_doc(commits, use_message=True, use_files=True):
    """
    Find commits that are documentation related.

    Parameters
    ----------
    commits : pd.DataFrame
        pandas dataframe containing the commits information.

    use_message : bool, optional, default: True

    use_files: bool, optional, default: True
    """
    is_doc_message = commits.message.apply(lambda x: "doc" in x.lower())
    is_doc_files = commits.added.apply(lambda x: "doc" in " ".join(x).lower())
    is_doc = is_doc_message | is_doc_files
    is_doc.rename("is_doc", inplace=True)
    return is_doc
