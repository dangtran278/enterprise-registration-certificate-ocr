from difflib import SequenceMatcher

import ocr
from ocr import ocr


def get_match(query, corpus, step=4, flex=3, case_sensitive=False, verbose=False):
    """Return best matching substring of corpus.

    Parameters
    ----------
    query : str
    corpus : str
    step : int
        Step size of first match-value scan through corpus. Can be thought of
        as a sort of "scan resolution". Should not exceed length of query.
    flex : int
        Max. left/right substring position adjustment value. Should not
        exceed length of query / 2.

    Outputs
    -------
    pos_left, pos_right: int
        Starting and ending indices of matching string
    """

    def _match(a, b):
        """Compact alias for SequenceMatcher."""
        return SequenceMatcher(None, a, b).ratio()

    def scan_corpus(step):
        """Return list of match values from corpus-wide scan."""
        match_values = []

        m = 0
        while m + qlen - step <= len(corpus):
            match_values.append(_match(query, corpus[m : m-1+qlen]))
            if verbose:
                print(query, "-", corpus[m: m + qlen], _match(query, corpus[m: m + qlen]))
            m += step

        return match_values

    def index_max(v):
        """Return index of max value."""
        return max(range(len(v)), key=v.__getitem__)

    def adjust_left_right_positions():
        """Return left/right positions for best string match."""
        # bp_* is synonym for 'Best Position Left/Right' and are adjusted 
        # to optimize bmv_*
        p_l, bp_l = [pos] * 2
        p_r, bp_r = [pos + qlen] * 2

        # bmv_* are declared here in case they are untouched in optimization
        bmv_l = match_values[p_l // step]
        bmv_r = match_values[p_l // step]

        for f in range(flex):
            ll = _match(query, corpus[p_l - f: p_r])
            if ll > bmv_l:
                bmv_l = ll
                bp_l = p_l - f

            lr = _match(query, corpus[p_l + f: p_r])
            if lr > bmv_l:
                bmv_l = lr
                bp_l = p_l + f

            rl = _match(query, corpus[p_l: p_r - f])
            if rl > bmv_r:
                bmv_r = rl
                bp_r = p_r - f

            rr = _match(query, corpus[p_l: p_r + f])
            if rr > bmv_r:
                bmv_r = rr
                bp_r = p_r + f

            if verbose:
                print("\n" + str(f))
                print("ll: -- value: %f -- snippet: %s" % (ll, corpus[p_l - f: p_r]))
                print("lr: -- value: %f -- snippet: %s" % (lr, corpus[p_l + f: p_r]))
                print("rl: -- value: %f -- snippet: %s" % (rl, corpus[p_l: p_r - f]))
                print("rr: -- value: %f -- snippet: %s" % (rl, corpus[p_l: p_r + f]))

        return bp_l, bp_r, _match(query, corpus[bp_l : bp_r])

    if not case_sensitive:
        query = query.lower()
        corpus = corpus.lower()

    qlen = len(query)

    if flex >= qlen/2:
        """Warning: flex exceeds length of query. Setting to default."""
        flex = 3

    match_values = scan_corpus(step)
    pos = index_max(match_values) * step

    pos_left, pos_right, match_value = adjust_left_right_positions()

    return pos_left, pos_right, match_value, query


def get_best_match(queries, corpus):
    matches = []
    best_match = (-1, -1, -1, "")
    for query in queries:
        matches.append(get_match(query, corpus, step=3, flex=4, case_sensitive=True))
    for match in matches:
        if match[2] > best_match[2]:
            best_match = match
    return best_match


def add2dict(text, pos):
    dic = {}
    prv_l, prv_r = pos[0][:2]
    for i in range(1, len(pos)):
        cur_l, cur_r = pos[i][:2]
        key = pos[i-1][3][:-2]
        val = text[prv_r:cur_l].replace('\n', '')
        dic.update({key : val})
        prv_l, prv_r = cur_l, cur_r
    dic.update({pos[-1][3][:-2] : text[prv_r:].replace('\n', '')})
    return dic


def extract(data):
    text = ocr(data)

    fields = [[["Số: "],
               ["Đăng ký lần đầu, "],
               ["Đăng ký thay đổi lần thứ , "],
               ["Mã số thuế: "],
               ["Chi cục thuế  "]],

              [["Tên hộ kinh doanh: "]],

              [["Địa chỉ trụ sở hộ kinh doanh: ", "Địa điểm kinh doanh: "],
               ["Điện thoại: "],
               ["Fax: "],
               ["Email: "],
               ["Website: "]],

              [["Ngành, nghề kinh doanh: "]],

              [["Vốn kinh doanh: "]],

              [["Chủ thể thành lập hộ kinh doanh: "]],

              [["Họ và tên: ", "Họ và tên cá nhân hoặc tên đại diện hộ gia đình: "],
               ["Giới tính: "],
               ["Sinh năm: ", "Năm sinh: ", "Sinh ngày: ", "Ngày sinh: "],
               ["Dân tộc: "],
               ["Quốc tịch: "],
               ["Loại giấy tờ pháp lý của cá nhân: ", "Loại giấy tờ chứng thực cá nhân: "],
               ["Số giấy tờ pháp lý của cá nhân: ", "Số giấy chứng thực cá nhân: "],
               ["Ngày cấp: "],
               ["Nơi cấp: ", "Cơ quan cấp: "],
               ["Địa chỉ thường trú: ", "Nơi đăng ký hộ khẩu thường trú: "],
               ["Địa chỉ liên lạc: ", "Chỗ ở hiện tại: "],
               ["Được cấp lại  "]],

              [["KT. TRƯỜNG PHÒNG  "]]]

    matches = []
    for region in fields:
        for field in region:
            match = get_best_match(field, text)
            if match[2] > 0.66:
                matches.append(match)
    edict = add2dict(text, matches)

    return edict
