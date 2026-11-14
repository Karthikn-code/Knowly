
import asyncio
import selectors

from sqlalchemy import select

from app.db.session import AsyncSessionLocal, engine
from app.models.document import Document
from app.services.rag_service import answer_question


async def main():
    async with AsyncSessionLocal() as db:
        # Find the previously uploaded test document.
        result = await db.execute(
            select(Document).where(
                Document.id == "dd5c4a30-582d-4ea8-b074-b70b7583c1af"
            )
        )
        document = result.scalar_one_or_none()

        if document is None:
            print("Test document not found.")
            return

        print("Document:", document.original_filename)
        print("Document ID:", document.id)

        question = "What does Knowly do with uploaded documents?"

        print("\nQuestion:", question)
        print("\nGenerating answer...\n")

        result = await answer_question(
            db=db,
            user_id=document.user_id,
            question=question,
            document_id=document.id,
        )

        print("ANSWER:")
        print(result["answer"])

        print("\nCITATIONS:")
        for citation in result["citations"]:
            print(citation)

        print("\nRETRIEVED CHUNKS:", len(result["retrieved_chunks"]))

        assert result["answer"].strip()
        assert result["citations"]
        assert result["retrieved_chunks"]

        print("\nRAG INTEGRATION TEST: PASSED")


try:
    asyncio.run(
        main(),
        loop_factory=lambda: asyncio.SelectorEventLoop(
            selectors.SelectSelector()
        ),
    )
finally:
    asyncio.run(
        engine.dispose(),
        loop_factory=lambda: asyncio.SelectorEventLoop(
            selectors.SelectSelector()
        ),
    )
