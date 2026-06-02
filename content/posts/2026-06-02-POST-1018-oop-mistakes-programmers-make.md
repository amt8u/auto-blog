+++
title       = "OOP Mistakes Programmers Keep Making"
description = "From God Objects to inheritance abuse — the OOP mistakes that silently rot your codebase. Real patterns, real fixes, from real codebases."
date        = "2026-06-02T18:48:23+05:30"
slug        = "oop-mistakes-programmers-make"
tags        = ["oop", "programming", "software-design", "clean-code"]
keywords    = ["OOP mistakes", "object oriented programming mistakes", "common OOP anti-patterns", "inheritance misuse", "God object", "SOLID violations"]
canonical   = "/posts/oop-mistakes-programmers-make/"
feature_image = "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1200&auto=format&fit=crop"
+++

OOP has been around for fifty years. Everyone in software has taken a course on it. Most have read about SOLID, inheritance, encapsulation, polymorphism. And yet — I keep seeing the same design mistakes in codebase after codebase, from startups to enterprise projects.

Knowing the theory is not the same as writing good OOP. Here's where it actually goes wrong.

## The God Object

Start a project, create a `UserService` class. Someone adds payment logic to it. Then notification handling. Then authentication checks. Six months later: a 2000-line file that does everything, depends on everything, and breaks every time anyone touches it.

**A class should have one, and only one, reason to change.** This is the Single Responsibility Principle [3]. And the God Object — a single class that accumulates excessive responsibilities — is its most direct violation [2].

The real problem isn't that the class is large. It's that it becomes impossible to test, maintain, or hand off. To unit test one method you have to mock half the application. Onboarding someone new to that class takes three hours of archaeology. Change anything in it and you're not sure what else breaks [1].

The fix is splitting. If your class has methods handling completely different concerns — say, persistence and email sending — those are two classes trapped in one file.

![god object split](/images/posts/oop-mistakes-programmers-make/god-object-split.svg)

## Inheritance Is Not a Code-Sharing Tool

This is the one that genuinely bothers me, because it's often taught wrong — or at least remembered wrong.

Inheritance should model an **"is-a" relationship**. A `Dog` is an `Animal`. A `SavingsAccount` is a `BankAccount`. That's what inheritance exists for [1].

What I see instead: a class has five useful methods, and rather than thinking about the design, someone just extends it to get access to those methods. The result is deep inheritance hierarchies, tight coupling between semantically unrelated classes, and codebases that take thirty minutes to trace a single function call [1].

The classic example is `Ostrich extends Bird`. `Bird` has a `fly()` method. Ostriches can't fly, so `Ostrich` overrides it and throws an `UnsupportedOperationException`. You just broke the **Liskov Substitution Principle** — a subclass must be substitutable for its parent without breaking the program [3][2].

This comes up constantly in real codebases, not just toy examples.

**Favor composition over inheritance** [4]. Instead of inheriting behavior, inject it:

```java
// Wrong — inherits just to override and break the contract
class Ostrich extends Bird {
    @Override
    public void fly() {
        throw new UnsupportedOperationException("Ostriches can't fly");
    }
}

// Better — behavior is composed, not inherited
class Ostrich {
    private MovementBehavior movement;

    public Ostrich() {
        this.movement = new RunningBehavior();
    }
}
```

The hierarchy becomes flatter, the behavior becomes swappable, and you stop fighting the design every time requirements change [4].

## Treating `public` As the Default

Encapsulation is one of the four pillars of OOP. Recite that back to any developer and they'll nod. Then go look at their code and find that half the fields are `public` and there are three global variables sitting at the top of the file [1].

It usually isn't deliberate. Marking something public is faster than thinking about what access level it actually needs. But as soon as something is public, other classes will access it. Now the internal state of your class is implicitly owned by the rest of the codebase and you can't change it without breaking things.

**Start private. Promote to protected or public only when necessary.** If you're unsure whether a method needs to be public, it probably doesn't [1].

Global variables are the extreme end of this problem. Once something is global, you've handed its control to the entire application. Tracking down where a global gets mutated is one of the least pleasant debugging experiences in programming.

## The Fat Interface Trap

The Interface Segregation Principle is the least-discussed one in the SOLID family, and probably the one I find violated most quietly [3].

**Clients should not be forced to implement interfaces they don't use** [3]. Without this discipline, you create one large `IDataManager` interface with `read()`, `write()`, `delete()`, `archive()`, and `export()`. Now every read-only service implementing it must also implement `write()`, `delete()`, `archive()`, and `export()` — even if it will never call them.

The result is classes full of empty method stubs or `throw new NotImplementedException()`. That's a design problem wearing the costume of a solution.

Split the interface. `IReader`, `IWriter`, `IArchiver`. Each class implements only what it actually needs.

## Copy-Paste Programming

This one feels harmless in the moment. Similar logic exists in two classes, it's just a few lines, and extracting it feels like overkill.

It isn't harmless [5]. One update, one missed location, one inconsistent bug fix — and the two copies diverge. Now there's a subtle difference in behavior between two parts of the application and nobody knows why it crept in [5].

**Don't repeat yourself.** If the same logic lives in two places, it belongs in one. And if you're copy-pasting between classes, it's usually a sign the original design was wrong — there's a shared concern waiting to become its own class.

## Over-Engineering the Abstraction

The flip side of everything above, and worth saying directly: SOLID principles and design patterns are tools, not goals.

I have seen codebases where a method that adds two numbers gets wrapped in a `CalculationStrategy` interface, a `CalculationStrategyFactory`, and a `CalculationStrategyFactoryProvider`. Not exaggerating [6].

**Abstractions should earn their existence.** Over-applying design patterns without a concrete reason makes code harder to read, not easier [7]. The biggest risk of over-applying SOLID is that simple logic now requires navigating five abstract classes and three levels of dependency injection before you understand what it does [7].

Design for the complexity you have. Not the complexity you might theoretically encounter someday.

## Quick Reference

| Mistake | What It Looks Like | Better Approach |
|---|---|---|
| God Object | One class with 10+ responsibilities | Split by Single Responsibility |
| Inheritance abuse | Extending a class to reuse code | Composition or delegation |
| LSP violation | Subclass overrides method with an exception | Redesign the hierarchy |
| No encapsulation | Public fields, global state everywhere | Private by default |
| Fat interface | One interface with 20 methods | Multiple focused interfaces |
| Copy-paste | Identical logic in multiple classes | Extract to a shared component |
| Over-abstraction | Strategy factory for simple addition | Add abstraction when complexity justifies it |

> End

## Sources
1. [3 Common Object-Oriented Programming Mistakes Junior Devs Make — DEV Community](https://dev.to/codemom/3-common-object-oriented-programming-mistakes-junior-devs-make-me2)
2. [OOP Pitfalls in Java – Anti-patterns You Should Avoid](https://prgrmmng.com/oop-pitfalls-java-anti-patterns)
3. [SOLID Design Principles Explained — DigitalOcean](https://www.digitalocean.com/community/conceptual-articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design)
4. [Composition over Inheritance — Wikipedia](https://en.wikipedia.org/wiki/Composition_over_inheritance)
5. [Anti-Patterns in OOP: What to Watch Out For — Ahmed Ashraf on Medium](https://medium.com/@ahmedashrafdev99/anti-patterns-in-oop-what-to-watch-out-for-54425fd1fd15)
6. [How the SOLID Principles Guide Object-Oriented Design — Youngjun Kim on Medium](https://medium.com/@youngjun_kim/how-the-solid-principles-guide-object-oriented-design-examples-of-violations-and-their-8bacac9dda23)
7. [When Using SOLID Principles May Not Be Appropriate — Baeldung](https://www.baeldung.com/cs/solid-principles-avoid)