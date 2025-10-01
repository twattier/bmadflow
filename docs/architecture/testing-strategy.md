# Testing Strategy

## Testing Pyramid

```
       E2E (Manual POC)
      /                \
     Integration Tests
    /                    \
   Frontend Unit (30%)  Backend Unit (50%)
```

**POC Targets:**
- Frontend: 30% coverage (critical components)
- Backend: 50% coverage (services, repositories, routes)
- E2E: Manual testing with pilot users

**Phase 2 Targets:**
- Frontend: 70%, Backend: 80%, E2E: Playwright automation

## Test Organization

**Frontend:** `apps/web/tests/` - Vitest + React Testing Library

**Backend:** `apps/api/tests/` - pytest + pytest-asyncio + httpx

## Example Tests

**Frontend Component Test:**
```typescript
describe('MarkdownRenderer', () => {
  it('renders markdown headings', () => {
    render(<MarkdownRenderer content="# Hello" />);
    expect(screen.getByRole('heading')).toHaveTextContent('Hello');
  });
});
```

**Backend API Test:**
```python
@pytest.mark.asyncio
async def test_create_project(client: AsyncClient):
    response = await client.post("/api/projects", json={"github_url": "https://github.com/owner/repo"})
    assert response.status_code == 201
    assert response.json()["name"] == "repo"
```

---
