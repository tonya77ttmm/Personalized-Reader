# Interview Review: Fixing Document Pagination

## Short summary

The reader showed only part of an uploaded text file. The file was stored correctly, but the backend split it into fixed 500-word pages while the browser displayed each page inside a much shorter screen area. Some words were below the visible area and were clipped. Moving to the next backend page skipped those hidden words.

The fix was to make the browser control the visual pages. The reader loads the full document, measures how tall the rendered text is, and shows one screen-height section at a time. The Previous and Next buttons move the reading area by one screen.

## What was the problem?

The upload and display path had two different meanings of “page”:

1. The backend made pages of 500 words. This is a data-based page: a fixed number of words saved and returned together.
2. The frontend showed text inside a fixed-height reading area. This is a visual page: the amount of text that fits on the user’s screen.

Those sizes did not match. A 500-word backend page could be taller than the reading area. The reading area used `overflow: hidden`, which clipped anything outside its visible bounds. The Next button then loaded the next 500-word page, so the clipped words seemed to be missing.

The original text was not necessarily lost. The mismatch was between how the backend grouped the text and how much the browser could display at one time.

## What was the solution?

The reader now uses the complete document content returned by the document endpoint. It no longer uses the backend’s fixed 500-word pages to decide what the reader shows as a screen page.

The frontend keeps a fixed-height viewport, which is the visible reading area. It measures:

```text
number of visual pages = rendered content height / viewport height
```

In the code, `scrollHeight` measures the full content height, including the part outside the visible area. `clientHeight` measures the visible viewport height. The result is rounded up so the final partial screen counts as a page.

When the user presses Next or Previous, the reader changes the viewport’s `scrollTop` by one viewport height. The viewport still shows one screen at a time, and the text is not discarded between pages. A `ResizeObserver` watches the viewport and content size, so page count is recalculated when the window size or text layout changes.

## Key terms in simple language

- **Pagination**: Dividing long content into sections that a reader can move through.
- **Data-based pagination**: Dividing data by a fixed count, such as 500 words per backend page.
- **Visual pagination**: Dividing content according to what fits in the available screen area.
- **Viewport**: The visible window where the document text appears.
- **`overflow: hidden`**: A CSS rule that hides anything extending beyond an element’s visible area. It can make text look missing if the content is too tall.
- **`scrollHeight`**: The height of all content inside an element, including content that is currently out of view.
- **`clientHeight`**: The visible inside height of an element. Here, it is the height of one screen page.
- **`scrollTop`**: How far the content has been moved vertically inside a scrollable element.
- **`ResizeObserver`**: A browser feature that notifies the app when an element’s size changes.
- **Responsive layout**: A layout that adjusts when the screen or reading area changes size.
- **State**: Data the UI remembers, such as the current page number. Updating state lets React redraw the interface.
- **API endpoint**: A server URL the frontend calls to get data. In this case, the document endpoint returns the uploaded document.

## What did I learn?

1. **Define what “page” means.** A backend page and a screen page are different things. A fixed word count does not guarantee that text fits on a screen.
2. **Follow the whole data path.** Check upload, storage, API response, frontend state, and rendering before deciding that data was lost.
3. **Measure the real layout.** Text height changes with screen width, font size, and line spacing. Visual pagination should use the browser’s measured layout rather than a guessed word count.
4. **Be careful with clipping.** `overflow: hidden` is useful for a clean page view, but it can hide content if the app does not provide a way to reach the rest.
5. **Test different situations.** Try short and long documents, different window sizes, and the first and last page. Confirm that all text can be reached and the page counter stays correct.

## Interview answer example

“I investigated a document reader where uploaded text appeared to be missing. The backend stored the whole file but divided it into fixed 500-word pages. The frontend showed each backend page in a fixed-height box with hidden overflow, so part of a page was clipped before the Next button moved to the following page. I changed the reader to load the full document and paginate by the actual rendered screen height. It measures the content and viewport, recalculates when their sizes change, and moves by one viewport when the user changes pages. The main lesson was to distinguish data pagination from visual pagination and measure the actual layout.”

## Files related to the fix

- `frontend/src/components/reader/DocumentViewer.tsx` — loads the document, measures visual page count, and handles page navigation.
- `backend/app/services/document_service.py` — stores the document and contains the original fixed 500-word backend splitting logic.
