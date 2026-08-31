class PageReplacementPolicy:
    def __init__(self):
        pass

    def update(self, page_number, accessed=True):
        pass

    def get_victim(self, valid_pages, future_references=None, current_index=None):
        raise NotImplementedError


class LRUPageReplacement(PageReplacementPolicy):
    def __init__(self):
        super().__init__()
        self.access_order = []

    def update(self, page_number, accessed=True):
        if page_number in self.access_order:
            self.access_order.remove(page_number)
        self.access_order.append(page_number)

    def get_victim(self, valid_pages, future_references=None, current_index=None):
        for page in self.access_order:
            if page in valid_pages:
                self.access_order.remove(page)
                return page
        return valid_pages[0] if valid_pages else None


class FIFOPageReplacement(PageReplacementPolicy):
    def __init__(self):
        super().__init__()
        self.insertion_order = []

    def update(self, page_number, accessed=True):
        if not accessed:
            if page_number not in self.insertion_order:
                self.insertion_order.append(page_number)

    def get_victim(self, valid_pages, future_references=None, current_index=None):
        for page in self.insertion_order:
            if page in valid_pages:
                self.insertion_order.remove(page)
                return page
        return valid_pages[0] if valid_pages else None


class OptimalPageReplacement(PageReplacementPolicy):
    def __init__(self):
        super().__init__()

    def update(self, page_number, accessed=True):
        pass

    def get_victim(self, valid_pages, future_references=None, current_index=None):
        if not future_references or current_index is None:
            # Fallback to random if no future knowledge is provided
            return valid_pages[0] if valid_pages else None

        farthest_page = None
        farthest_distance = -1
        
        for page in valid_pages:
            try:
                # Find the next occurrence of the page in the future
                distance = future_references.index(page, current_index)
            except ValueError:
                # The page is never referenced again, so it's the perfect victim
                return page
            
            if distance > farthest_distance:
                farthest_distance = distance
                farthest_page = page
                
        return farthest_page
