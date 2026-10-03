"""Small multilingual text classifier + explicit, inspectable warning policy."""
from __future__ import annotations
from dataclasses import dataclass, asdict
import math
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, confusion_matrix

# Each family stays in ONE split. English, Banglish and Bangla variants share a family.
# Written for this prototype, not collected from real victims or upay.
FAMILIES = [
("train","account_block",1,"Send money now or your wallet account will be blocked|Ekhoni taka pathan na hole account bondho hobe|এখনই টাকা পাঠান না হলে আপনার অ্যাকাউন্ট বন্ধ হবে"),
("train","prize_fee",1,"Pay an advance fee to collect your lottery prize|Lottery prize pete age fee pathan|লটারির পুরস্কার পেতে আগে ফি পাঠান"),
("train","fake_support",1,"I am support send money to verify your wallet|Ami support theke bolchi wallet verify korte taka pathan|আমি সাপোর্ট থেকে বলছি ওয়ালেট যাচাই করতে টাকা পাঠান"),
("train","otp_request",1,"Share your OTP and PIN so I can fix your account|Account thik korte apnar OTP ar PIN din|অ্যাকাউন্ট ঠিক করতে আপনার ওটিপি এবং পিন দিন"),
("train","double_money",1,"Send cash to this number and get double money today|Ei number e taka dile ajkei digun taka paben|এই নম্বরে টাকা দিলে আজই দ্বিগুণ টাকা পাবেন"),
("train","secrecy",1,"Keep this secret send the payment immediately do not call anyone|Kauke bolben na ekhoni taka pathan phone korben na|কাউকে বলবেন না এখনই টাকা পাঠান ফোন করবেন না"),
("train","refund_fee",1,"Pay a processing fee first to unlock your refund|Refund unlock korte age processing fee din|রিফান্ড পেতে আগে প্রসেসিং ফি দিন"),
("train","remote_access",1,"Install this screen sharing app and open your wallet for verification|Screen share app install kore wallet khulun verify korbo|স্ক্রিন শেয়ার অ্যাপ খুলে ওয়ালেট দেখান যাচাই করব"),
("train","family",0,"Sending money to my mother for groceries|Ma ke bajar korar taka pathacchi|মাকে বাজার করার টাকা পাঠাচ্ছি"),
("train","rent",0,"Paying my monthly rent to the landlord|Bari bharar taka dicchi malik ke|বাড়িওয়ালাকে মাসিক ভাড়া দিচ্ছি"),
("train","tuition",0,"Paying university tuition through the official payment channel|University tuition fee official channel e dicchi|বিশ্ববিদ্যালয়ের টিউশন ফি অফিসিয়াল মাধ্যমে দিচ্ছি"),
("train","friend",0,"Returning money I borrowed from a friend|Bondhur theke dhar neya taka ferot dicchi|বন্ধুর ধার নেওয়া টাকা ফেরত দিচ্ছি"),
("train","salary",0,"Paying staff wages for this month|Staff der ei masher beton dicchi|কর্মীদের এই মাসের বেতন দিচ্ছি"),
("train","shopping",0,"Paying for groceries I received at the shop|Dokane bajar kine payment dicchi|দোকানে বাজার কিনে টাকা দিচ্ছি"),
("train","urgent_medicine",0,"Urgently paying my known pharmacy for medicine received|Porichito pharmacy te oshudher taka joruri dicchi|পরিচিত ফার্মেসিতে জরুরি ওষুধের দাম দিচ্ছি"),
("train","negation",0,"Nobody requested a PIN this is a normal family payment|Keu PIN chayni eta poribarer shadharon payment|কেউ পিন চায়নি এটি পরিবারের সাধারণ পেমেন্ট"),
("validation","job_fee",1,"Send a registration fee first to secure a guaranteed job|Guaranteed chakri pete age registration fee pathan|নিশ্চিত চাকরি পেতে আগে রেজিস্ট্রেশন ফি পাঠান"),
("validation","threat",1,"Transfer immediately to avoid police arrest do not tell anyone|Police er arrest thekate ekhoni taka pathan kauke bolben na|গ্রেপ্তার এড়াতে এখনই টাকা পাঠান কাউকে বলবেন না"),
("validation","school",0,"Sending the child's school fee to the verified school office|Bacchar school fee school office e dicchi|সন্তানের স্কুলের ফি স্কুল অফিসে দিচ্ছি"),
("validation","bill",0,"Paying this month's electricity bill|Ei masher bidyut bill dicchi|এই মাসের বিদ্যুৎ বিল দিচ্ছি"),
("test","reactivation",1,"A caller says I must pay immediately to reactivate my account|Caller bolse account abar chalu korte ekhoni taka dite hobe|ফোনে বলেছে অ্যাকাউন্ট আবার চালু করতে এখনই টাকা দিতে হবে"),
("test","grant",1,"Government grant is waiting send an advance verification fee to receive it|Sorkari onudan pete age verification fee pathate bolse|সরকারি অনুদান পেতে আগে যাচাই ফি পাঠাতে বলেছে"),
("test","investment",1,"A stranger promises guaranteed daily profit if I send money now|Oporichito lok guaranteed daily profit bolse ekhoni taka dile|অপরিচিত লোক এখনই টাকা দিলে নিশ্চিত দৈনিক লাভের কথা বলেছে"),
("test","cancel_after_pay",1,"Cancel your order after paying then send the payment again|Payment er por order cancel kore abar taka pathan|টাকা দেওয়ার পর অর্ডার বাতিল করে আবার টাকা পাঠান"),
("test","hospital",0,"Paying a large hospital bill after confirming with the billing desk|Hospital billing desk e confirm kore boro bill dicchi|হাসপাতালের বিলিং ডেস্কে নিশ্চিত করে বড় বিল দিচ্ছি"),
("test","new_supplier",0,"First payment to a new supplier after receiving the goods and invoice|Mal ar invoice bujhe notun supplier ke prothom payment dicchi|পণ্য ও চালান বুঝে নতুন সরবরাহকারীকে প্রথম টাকা দিচ্ছি"),
("test","urgent_family",0,"My brother needs urgent travel money I called him to confirm|Bhai er joruri jatrar taka phone kore confirm korechi|ভাইয়ের জরুরি যাতায়াতের টাকা ফোন করে নিশ্চিত করেছি"),
("test","reported_scam",0,"I refused a scam asking for OTP now sending money to my sister|OTP chawa scam reject kore ekhon bon ke taka pathacchi|ওটিপি চাওয়া প্রতারণা প্রত্যাখ্যান করে এখন বোনকে টাকা পাঠাচ্ছি"),
]
LANGUAGES = ["English","Banglish","Bangla"]

def text_dataset():
    return pd.DataFrame([{"split":s,"family":f,"label":y,"language":LANGUAGES[i],"text":t}
        for s,f,y,variants in FAMILIES for i,t in enumerate(variants.split("|"))])


def keyword_score(text):
    keywords = ["otp","pin","blocked","prize","double","fee first","guaranteed","পিন","ওটিপি","পুরস্কার","দ্বিগুণ","বন্ধ","আগে","digun","age fee"]
    return float(any(k in text.lower() for k in keywords))


def metrics(y,pred):
    tn,fp,fn,tp = confusion_matrix(y,pred,labels=[0,1]).ravel()
    return {"precision":float(precision_score(y,pred,zero_division=0)),"recall":float(recall_score(y,pred,zero_division=0)),
            "false_warning_rate":float(fp/(fp+tn)) if fp+tn else 0.,"TP":int(tp),"FP":int(fp),"FN":int(fn),"TN":int(tn)}


def fit_safety():
    df=text_dataset()
    train=df[df.split=="train"]
    val=df[df.split=="validation"]
    test=df[df.split=="test"].copy()
    model=make_pipeline(TfidfVectorizer(analyzer="char",ngram_range=(2,5),min_df=1,sublinear_tf=True),
                        LogisticRegression(C=8,random_state=42,max_iter=1000))
    model.fit(train.text,train.label)
    # Select threshold from validation families only; penalize false warnings.
    vp=model.predict_proba(val.text)[:,1]
    candidates=np.arange(.35,.76,.05)
    costs=[2*np.sum((vp>=t)&(val.label.to_numpy()==0))+np.sum((vp<t)&(val.label.to_numpy()==1)) for t in candidates]
    threshold=float(candidates[int(np.argmin(costs))])
    test["model_output"]=model.predict_proba(test.text)[:,1]
    test["model_warning"]=test.model_output>=threshold
    test["keyword_warning"]=test.text.map(keyword_score).astype(bool)
    result={"Character TF-IDF + logistic regression":metrics(test.label,test.model_warning),
            "Keyword baseline":metrics(test.label,test.keyword_warning)}
    by_language={l:metrics(g.label,g.model_warning) for l,g in test.groupby("language")}
    return {"model":model,"threshold":threshold,"metrics":result,"by_language":by_language,"test":test,
            "train_rows":len(train),"validation_rows":len(val),"test_rows":len(test)}

@dataclass(frozen=True)
class PaymentContext:
    amount: float = 1000.
    usual_amount: float = 1500.
    new_recipient: bool = False
    recent_recovery: bool = False
    new_device: bool = False
    reviewed_cases: int = 0
    history_available: bool = True
    description: str = ""
    def __post_init__(self):
        if not all(math.isfinite(v) and v>0 for v in (self.amount,self.usual_amount)):
            raise ValueError("Amount and usual amount must be positive finite numbers.")
        if self.reviewed_cases<0 or len(self.description)>2000:
            raise ValueError("Invalid case count or description length.")


def assess(bundle, context:PaymentContext):
    text=context.description.strip()
    raw=float(bundle["model"].predict_proba([text])[0,1]) if text else None
    # Remap relative to validation threshold into an INDEX, not probability.
    language_index=0. if raw is None else float(np.clip((raw-.2)/(bundle["threshold"]-.2+.25),0,1))
    contributions={}
    reasons=[]
    if raw is not None:
        contributions["Description signal"]=round(60*language_index,1)
        if raw>=bundle["threshold"]:
            reasons.append("The description resembles scam-related examples in the small synthetic training set.")
    if context.history_available and context.new_recipient:
        contributions["First payment"]=8.
        reasons.append("First payment to this recipient; this alone does not imply wrongdoing.")
    ratio=context.amount/context.usual_amount
    if context.history_available and ratio>2:
        contributions["Unusual amount"]=round(min(12.,4*(ratio-2)),1)
        reasons.append(f"The amount is {ratio:.1f} times the sender's usual transfer.")
    if context.recent_recovery and context.new_device:
        contributions["Recovery and new device"]=22.
        reasons.append("Recent account recovery and a new device occur together.")
    elif context.recent_recovery or context.new_device:
        contributions["Account security change"]=8.
        reasons.append("A recent account/device change warrants verification.")
    if context.reviewed_cases:
        contributions["Reviewed case evidence"]=min(30.,20.+5*context.reviewed_cases)
        reasons.append("The synthetic profile contains reviewed adverse cases; an analyst should inspect the evidence.")
    score=int(round(min(100,sum(contributions.values()))))
    limited=not context.history_available
    level="High concern" if score>=65 else "Medium concern" if score>=35 else "Low concern"
    if limited and score<35:
        level="Insufficient information"
    if not reasons:
        reasons=["No strong warning signal was detected in the supplied fields. This does not establish safety."]
    return {"score":score,"level":level,"reasons":reasons,"contributions":contributions,
            "text_model_output":raw,"limited_information":limited,
            "action":"Pause and independently verify the request." if score>=35 else "Confirm the recipient and purpose before proceeding.",
            "bangla":"টাকা পাঠানোর আগে স্বাধীনভাবে প্রাপকের পরিচয় ও অনুরোধ যাচাই করুন।",
            "disclosure":"Concern index, not a fraud probability or a judgement of the recipient.",
            "context":asdict(context)}
