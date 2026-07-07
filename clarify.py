from gemini_client import client

def needs_clarification(query: str) -> str | None:
    """Sorğu qeyri-müəyyəndirsə, aydınlaşdırıcı sual qaytarır. Aydındırsa None qaytarır."""
    prompt = f"""Sən bir e-commerce axtarış köməkçisisən. İstifadəçinin sorğusu: "{query}"

Əgər bu sorğu axtarış nəticələrini yaxşılaşdırmaq üçün BİR aydınlaşdırıcı sual tələb edəcək qədər qeyri-müəyyəndirsə (məsələn hədəf qrup, mövsüm, büdcə bəlli deyilsə), YALNIZ o sualı Azərbaycan dilində yaz.

Əgər sorğu artıq kifayət qədər aydındırsa, YALNIZ bu sözü yaz: NO_CLARIFICATION

Başqa heç nə yazma."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    result = response.text.strip()
    return None if "NO_CLARIFICATION" in result else result


def merge_query(original_query: str, clarification_answer: str) -> str:
    """Orijinal sorğu ilə istifadəçinin cavabını birləşdirib zənginləşdirilmiş sorğu yaradır."""
    prompt = f"""Orijinal axtarış sorğusu: "{original_query}"
İstifadəçinin əlavə cavabı: "{clarification_answer}"

Bu ikisini birləşdirərək, vector axtarışı üçün yaxşı, təsviri bir sorğu cümləsi yaz (Azərbaycan dilində, YALNIZ cümləni yaz, başqa heç nə)."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text.strip()