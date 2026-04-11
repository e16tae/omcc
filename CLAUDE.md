# omcc (oh-my-claude-code)

개인 Claude Code 플러그인 마켓플레이스.
외부 플러그인을 큐레이팅하여 한 곳에서 설치 가능하게 하고,
향후 자체 플러그인도 호스팅한다.

## 구조
- `.claude-plugin/marketplace.json` — 마켓플레이스 매니페스트 (핵심)
- `plugins/` — 자체 빌트인 플러그인
- `scripts/` — CI 및 로컬 실행용 검증 스크립트
- `tests/` — pytest 기반 마켓플레이스 검증 테스트
- `pyproject.toml` — 프로젝트 설정 및 테스트 의존성
- `.github/workflows/` — CI (검증 + 릴리스 자동화)

## marketplace.json 편집 규칙
- 항상 유효한 JSON 유지
- plugins 배열은 name 기준 알파벳 오름차순 정렬
- 플러그인 엔트리 필수 필드: name, description, source
- 선택 필드: category, homepage, version, author
- 검증: `uv run --extra test pytest` 또는 `python3 -m json.tool .claude-plugin/marketplace.json`

## 플러그인 추가 절차
1. 소스 repo가 public이고 .claude-plugin/plugin.json 존재 확인
2. 유지보수 활성 또는 명시적 안정 상태 확인
3. OSI 승인 라이선스 확인
4. 기존 플러그인과 기능 중복 없음 확인
5. 로컬 테스트
6. marketplace.json의 plugins 배열에 엔트리 추가 (알파벳 위치에 삽입)

## Source Type 선택
- git-subdir: 플러그인이 모노레포 서브디렉토리에 위치 시
- url: 플러그인이 repo 루트에 위치 시
- ./plugins/...: omcc 내 자체 플러그인

## Commit Convention (Conventional Commits)

`<type>(<scope>): <description>`

Types: `feat`, `fix`, `docs`, `ci`, `refactor`, `chore`
Scope: 플러그인 이름 또는 영역

- 플러그인 추가: `feat(name): add ...`
- 플러그인 수정: `fix(name): update ...`
- 플러그인 제거: `feat(name)!: remove ...` (BREAKING CHANGE)
- 문서/CI: `docs(...)`, `ci(...)`

## Versioning
- SemVer (MAJOR.MINOR.PATCH)
- MAJOR: breaking change (플러그인 제거/이름 변경)
- MINOR: 플러그인 추가
- PATCH: 설명 수정 등
- release-please가 커밋 메시지 기반으로 자동 관리
