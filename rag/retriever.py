"""
Enterprise SRE RAG (Retrieval-Augmented Generation) Indexer & Semantic Retriever
Author: Shruti Bawase
"""

import math
import re
from typing import List, Dict, Any

SAMPLE_RUNBOOKS = [
    {
        "id": "RB-001",
        "title": "Kubernetes Pod OOMKilled (Exit Code 137) Remediation",
        "content": "When a pod exits with status code 137, the Linux kernel OOM killer terminated the process. Immediate steps: 1. Check container memory limits using kubectl describe pod. 2. Verify JVM heap options (-Xmx). 3. Increase resource limits in Helm values.yaml by 50%. 4. Apply Horizontal Pod Autoscaler based on memory metric."
    },
    {
        "id": "RB-002",
        "title": "Terraform Out-of-Band State Drift Remediation",
        "content": "When manual changes occur in Azure portal causing state drift: 1. Run terraform plan -detailed-exitcode. 2. Compare live resource attributes against git commit history. 3. If change was unauthorized, execute terraform apply to overwrite drift. 4. If change is legitimate, backport resource changes to IaC repo and open PR."
    },
    {
        "id": "RB-003",
        "title": "Azure Firewall TLS Inspection Failure & Certificate Renewal",
        "content": "If application egress fails with SSL handshake timeouts: 1. Verify intermediate CA validity in Azure Key Vault. 2. Check Azure Firewall Premium Policy rule matching for TLS inspection. 3. Renew expired certificates in Key Vault and force firewall policy resync."
    }
]

def tokenize(text: str) -> List[str]:
    return re.findall(r"\w+", text.lower())

class SRERetriever:
    def __init__(self, runbooks: List[Dict[str, str]] = SAMPLE_RUNBOOKS):
        self.runbooks = runbooks
        self.vocab = set()
        for doc in self.runbooks:
            self.vocab.update(tokenize(doc["title"] + " " + doc["content"]))

    def _vectorize(self, text: str) -> Dict[str, float]:
        tokens = tokenize(text)
        tf = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        return tf

    def search(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        query_vec = self._vectorize(query)
        scored_docs = []

        for doc in self.runbooks:
            doc_vec = self._vectorize(doc["title"] + " " + doc["content"])
            dot_product = sum(query_vec.get(term, 0) * doc_vec.get(term, 0) for term in query_vec)
            norm_q = math.sqrt(sum(v ** 2 for v in query_vec.values())) or 1.0
            norm_d = math.sqrt(sum(v ** 2 for v in doc_vec.values())) or 1.0
            score = dot_product / (norm_q * norm_d)
            if score > 0:
                scored_docs.append({
                    "score": round(score, 4),
                    "id": doc["id"],
                    "title": doc["title"],
                    "content": doc["content"]
                })

        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        return scored_docs[:top_k]
