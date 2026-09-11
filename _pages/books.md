---
layout: page
title: bookshelf
permalink: /books/
nav: false
collection: books
---

> What an astonishing thing a book is. It's a flat object made from a tree with flexible parts on which are imprinted lots of funny dark squiggles. But one glance at it and you're inside the mind of another person, maybe somebody dead for thousands of years. Across the millennia, an author is speaking clearly and silently inside your head, directly to you. Writing is perhaps the greatest of human inventions, binding together people who never knew each other, citizens of distant epochs. Books break the shackles of time. A book is proof that humans are capable of working magic.
>
> -- Carl Sagan, Cosmos, Part 11: The Persistence of Memory (1980)

## Books that I am reading, have read, or will read

<style>
.books-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
}
.book-item {
  width: 140px;
  text-align: center;
}
.book-cover {
  width: 100%;
  height: 210px;
  object-fit: cover;
  border-radius: 5px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  transition: transform 0.2s ease-in-out;
}
.book-item a {
  text-decoration: none;
  color: var(--global-text-color);
}
.book-item a:hover .book-cover {
  transform: scale(1.05);
}
.book-item a:hover {
  text-decoration: none;
}
.book-title {
  margin-top: 10px;
  font-weight: 600;
  font-size: 0.9em;
  line-height: 1.3;
}
.year-heading {
  margin-top: 3rem;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid var(--global-divider-color, #e5e5e5);
  padding-bottom: 0.5rem;
  font-size: 1.5rem;
  font-weight: bold;
}
</style>

{% assign pre_books = "" | split: "" %}
{% assign dated_books = "" | split: "" %}

{% for book in site.books %}
  {% if book.finished or book.started %}
    {% assign dated_books = dated_books | push: book %}
  {% else %}
    {% assign pre_books = pre_books | push: book %}
  {% endif %}
{% endfor %}

{% assign books_by_year = dated_books | group_by_exp: "item", "item.finished | default: item.started | slice: 0, 4" | sort: "name" | reverse %}

<div class="bookshelf">
  {% for group in books_by_year %}
    <h3 class="year-heading">
      {{ group.name }} 
      <span style="font-size: 0.6em; color: var(--global-text-color-light, #888); font-weight: normal;">({{ group.size }} {% if group.size == 1 %}book{% else %}books{% endif %})</span>
    </h3>
    <div class="books-grid">
      {% assign sorted_items = group.items | sort: "finished" | reverse %}
      {% for book in sorted_items %}
        <div class="book-item">
          <a href="{{ book.url | relative_url }}">
            {% if book.cover %}
              <img src="{{ book.cover | relative_url }}" alt="{{ book.title }} cover" class="book-cover">
            {% else %}
              <div class="book-cover" style="display:flex;align-items:center;justify-content:center;background:#eee;color:#999;">No Cover</div>
            {% endif %}
            <div class="book-title">{{ book.title }}</div>
          </a>
        </div>
      {% endfor %}
    </div>
  {% endfor %}

  {% if pre_books.size > 0 %}
    <h3 class="year-heading">
      Pre-2026 
      <span style="font-size: 0.6em; color: var(--global-text-color-light, #888); font-weight: normal;">({{ pre_books.size }} {% if pre_books.size == 1 %}book{% else %}books{% endif %})</span>
    </h3>
    <div class="books-grid">
      {% for book in pre_books %}
        <div class="book-item">
          <a href="{{ book.url | relative_url }}">
            {% if book.cover %}
              <img src="{{ book.cover | relative_url }}" alt="{{ book.title }} cover" class="book-cover">
            {% else %}
              <div class="book-cover" style="display:flex;align-items:center;justify-content:center;background:#eee;color:#999;">No Cover</div>
            {% endif %}
            <div class="book-title">{{ book.title }}</div>
          </a>
        </div>
      {% endfor %}
    </div>
  {% endif %}
</div>
