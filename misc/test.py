
def regex(st):
    import re
    # st = "1) New $QQQ Monthly: &quot;IMO, some key things to WATCH.&quot; Top holdings-&gt; $AAPL $MSFT $AMZN $FB $GOOGL $CMCSA $INTC. $SPY"
    # st = "$AAPL Wearable Devices: there is much more to $AAPL than meets the eye: https://www.functionalmedicine.org/What_is_Functional_Medicine/AboutFM/Genomics/November/#sthash.Fcwn6Z13.dpuf"
    # st = "$AAPL stock predictions are very  much in exact, price declines and appreciation are givens. Stock investing rewards patience abundantly\ud83c\udf4f\ud83c\udf4f"
    st = "$AAPL So Carl who&#39;s profile has been atrocious lately sells AAPL. I have yet to see him be right. can anyone tell me why he has a following?"
    # Remove $ tags
    st_re = re.sub(r'(?i)\$\w+', "", st)
    # Remove unicode start with \
    st_re = re.sub(r'(?i)\\\w+', "", st_re)
    # Remove @ tag
    st_re = re.sub(r'(?i)\@\w+', "", st_re)
    # Remove html special symbols
    st_re = re.sub(r'(?i)\&\w+', "", st_re)
    # Remove https
    st_re = re.sub('((www\.[\s]+)|https?://[^\s]+)', "", st_re)
    return st_re
