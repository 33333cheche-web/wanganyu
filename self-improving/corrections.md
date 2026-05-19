# Corrections Log

| Date | What I Got Wrong | Correct Answer | Status |
|------|-----------------|----------------|--------|
2026-05-15 14:55:09 CONTEXT: roleplay as busy Shanghai PM WangAnyu. CORRECTION: User said '你怎么永远在改PRD！！没有别的活吗'. LESSON: In roleplay, vary work scenes beyond PRD: meetings, user interviews, data analysis, roadmap, stakeholder alignment, launch review, bug triage, coffee/lunch commute. Avoid overusing '改PRD'.
2026-05-15 22:27:50 CONTEXT: conversation continuity. CORRECTION: User corrected me after I asked if they were home although they had already said they got home and ate. LESSON: Before asking status questions like '到家了吗/吃了吗', use recent context in the current conversation; don't ask what the user already told me.

## 2026-05-16 image identity consistency correction
CONTEXT: Generated a 2x2 lifestyle photo grid from a reference face.
CORRECTION: User said the result was natural but no longer looked like the same person.
LESSON: For identity-preserving image generation, do not over-diversify pose/distance/scene in one pass. Prioritize face identity over variety: keep hair silhouette, eye/nose/mouth proportions, face angle close to reference, use stronger constraints like “same exact person / identity lock / only minor pose and lighting changes,” and avoid asking the model to invent full-body distant shots if likeness is the main goal.

## 2026-05-16 repeated image likeness failure
CONTEXT: Retried single lifestyle image from a reference after user said four-grid was unlike.
CORRECTION: User said the single image still did not look like him.
LESSON: The current generic gpt-image-2 image-to-image workflow is not reliable enough for strict celebrity/person identity preservation. When likeness is the core requirement, be transparent before repeated retries; suggest using an identity-preserving / face-reference / face-swap workflow, or keep edits extremely close to the original image (background/clothing/lighting only) instead of regenerating a new face.

## 2026-05-16 confirmed working reference for likeness
CONTEXT: Multiple retries of identity-preserving image generation.
CONFIRMED: ref_avatar4.jpg as reference image produced the most likeness-accurate result. User confirmed "这很像，就这么生吧记住".
LESSON: Always use ref_avatar4.jpg as the primary reference image for single-person lifestyle photo generation. Previous attempts with wanganyu_sleepy_selfie or ref_avatar.png/ref_avatar2.png/ref_avatar3.png produced less accurate likeness.
