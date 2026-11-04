// The page has one question box; the skip link and the chat send the keyboard back to it
export const QUESTION_BOX_ID = 'question-box';

/** Move the keyboard to the question box, after a control that started a question goes away. */
export function focusQuestionBox(): void {
  document.getElementById(QUESTION_BOX_ID)?.focus();
}
