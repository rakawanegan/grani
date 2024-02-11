import tenseal as ts
import pandas as pd
import joblib
from sklearn.preprocessing import OrdinalEncoder
from functools import partial


# Create the TenSEAL security context
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

def doc2vec(x, model, tokenizer):
    return None
    return model.infer_vector(tokenizer(x))

def df2num(rawdf, document_columns, string_columns):
    df = rawdf.copy()
    tokenizer = ""
    model = ""
    _doc2vec = partial(doc2vec, model=model, tokenizer=tokenizer)
    if model == "":
        df = df.drop(columns=document_columns, axis=1)
    else:
        df[document_columns] = df[document_columns].map(_doc2vec)
    oe = OrdinalEncoder()
    df[string_columns] = oe.fit_transform(df[string_columns]).astype(int)
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