"""发音评分服务"""
from difflib import SequenceMatcher


def score_pronunciation(expected_text: str, recognized_text: str) -> dict:
    """
    对比预期文本和识别文本，计算发音评分。
    返回单词级别的评分结果。
    """
    expected_words = expected_text.lower().strip().split()
    recognized_words = recognized_text.lower().strip().split()

    # 整体相似度
    similarity = SequenceMatcher(None, expected_text.lower(), recognized_text.lower()).ratio()
    overall_score = round(similarity * 100)

    # 单词级评分
    word_scores = []
    for ew in expected_words:
        best_match = 0
        matched_word = ""
        for rw in recognized_words:
            s = SequenceMatcher(None, ew, rw).ratio()
            if s > best_match:
                best_match = s
                matched_word = rw
        score = round(best_match * 100)
        word_scores.append({
            "word": ew,
            "score": score,
            "level": _score_level(score),
        })

    # 计算级别分布
    excellent = sum(1 for w in word_scores if w["level"] == "excellent")
    good = sum(1 for w in word_scores if w["level"] == "good")
    needs_work = sum(1 for w in word_scores if w["level"] == "needs_work")

    return {
        "overall_score": overall_score,
        "overall_level": _score_level(overall_score),
        "expected_text": expected_text,
        "recognized_text": recognized_text,
        "word_scores": word_scores,
        "stats": {
            "excellent": excellent,
            "good": good,
            "needs_work": needs_work,
            "total": len(word_scores),
        },
        "fluency": round(min(similarity * 1.1, 1.0) * 100),
        "accuracy": overall_score,
    }


def _score_level(score: int) -> str:
    if score >= 85:
        return "excellent"
    elif score >= 60:
        return "good"
    else:
        return "needs_work"
