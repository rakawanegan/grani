import pandas as pd
import joblib
from janome.tokenizer import Tokenizer
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sklearn.preprocessing import OrdinalEncoder
from functools import partial
import tenseal as ts

def create_ctx():
    """Helper for creating the CKKS context.
    CKKS params:
        - Polynomial degree: 8192.
        - Coefficient modulus size: [40, 21, 21, 21, 21, 21, 21, 40].
        - Scale: 2 ** 21.
        - The setup requires the Galois keys for evaluating the convolutions.
    """
    poly_mod_degree = 8192
    coeff_mod_bit_sizes = [40, 21, 21, 21, 21, 21, 21, 40]
    ctx = ts.context(ts.SCHEME_TYPE.CKKS, poly_mod_degree, -1, coeff_mod_bit_sizes)
    ctx.global_scale = 2 ** 21
    ctx.generate_galois_keys()
    ctx.generate_relin_keys()
    return ctx

def tenseal_save(enclist, filename="enc-data/main"):
    metaenclist = list()
    with open(f"{filename}.tso", "wb") as f:
        for data in enclist:
            data = data.serialize()
            f.write(data)
            metaenclist.append(len(data))
    joblib.dump(metaenclist, f"{filename}-meta.joblib")

def expand_arrays(df):
    # 入れ子の配列を展開する関数
    def flatten_array(arr):
        return pd.Series(arr)

    # 各列を処理
    expanded_df = pd.DataFrame()
    for col in df.columns:
        if isinstance(df[col][0], list):
            expanded_col = df[col].apply(flatten_array)
            expanded_col.columns = [f"{col}_{i}" for i in range(len(expanded_col.iloc[0]))]
            expanded_df = pd.concat([expanded_df, expanded_col], axis=1)
        else:
            expanded_df[col] = df[col]
    return expanded_df


def df2num(rawdf, document_columns, string_columns):
    EMBEDDING_DIM = 512

    def _doc2vec(x, model, tokenizer):
        tokens = [token.surface for token in tokenizer.tokenize(x)]
        return model.infer_vector(tokens)
    df = rawdf.copy()
    tokenizer = Tokenizer()
    for document_column in document_columns:
        tagged_data = [TaggedDocument(words=[token.surface for token in tokenizer.tokenize(doc)], tags=[str(i)]) for i, doc in enumerate(df[document_column].values)]
        model = Doc2Vec(vector_size=EMBEDDING_DIM, window=10, min_count=1, workers=4)
        model.build_vocab(tagged_data)
        model.train(tagged_data, total_examples=model.corpus_count, epochs=model.epochs)
        doc2vec = partial(_doc2vec, model=model, tokenizer=tokenizer)
        doclist = df[document_column].apply(doc2vec).tolist()
        docdf = pd.DataFrame(doclist, index=df.index)
        docdf.columns = [f"{document_column}_{i}" for i in range(EMBEDDING_DIM)]
        df = pd.concat([df, docdf], axis=1)
    df = df.drop(columns=document_columns)        
    oe = OrdinalEncoder()
    df[string_columns] = oe.fit_transform(df[string_columns]).astype(int)
    # df.to_csv("enc-data/numerical.csv", index=False)
    return df, oe

def df2enc(df, ctx,):
    enclist = list()
    for i, row in df.iterrows():
        rawdata = row.values
        encdata = ts.ckks_vector(ctx, rawdata)
        enclist.append(encdata)
    return enclist

def wrap_enc(
        inputpath='raw-data/健康習慣.csv',
        filename="enc-data/main",
        document_columns=["日常生活で心がけている健康習慣はどんなものですか？"],
        string_columns=["最も好きな運動は何ですか？"],
        ):
    inputdf = pd.read_csv(inputpath)
    df, oe = df2num(inputdf, document_columns, string_columns)
    context = create_ctx()
    with open("enc-data/context.joblib", "wb") as f:
        f.write(context.serialize(save_secret_key=True))
    pubctx = context.copy()
    pubctx.make_context_public()
    del context
    enclist = df2enc(df, pubctx,)
    joblib.dump(pubctx.serialize(), "enc-data/public_context.joblib")
    joblib.dump(oe, "enc-data/ordinalencoder.joblib")
    tenseal_save(enclist, filename)

if __name__ == "__main__":
    wrap_enc()
    print("Done")
